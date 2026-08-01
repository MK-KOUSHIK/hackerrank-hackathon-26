from .agent_tools import RouterTools
from .scorer import Scorer

class AgenticNotificationRouter:
    """
    Autonomous Agentic Router that dynamically invokes domain tools 
    (media OCR/ASR, user context, business history, safety check, historical evidence)
    to decide on WhatsApp message routing.
    """
    def __init__(self, dataset_dir):
        self.tools = RouterTools(dataset_dir)
        self.scorer = Scorer()

    def route_message(self, msg_row):
        message_id = str(msg_row["message_id"])
        user_id = str(msg_row["user_id"]) if "user_id" in msg_row and msg_row["user_id"] else None
        conv_type = str(msg_row["conversation_type"]) if "conversation_type" in msg_row else ""
        group_id = str(msg_row["group_id"]) if "group_id" in msg_row and msg_row["group_id"] else None
        business_id = str(msg_row["business_id"]) if "business_id" in msg_row and msg_row["business_id"] else None
        sender_user_id = str(msg_row["sender_user_id"]) if "sender_user_id" in msg_row and msg_row["sender_user_id"] else None
        
        raw_text = str(msg_row["message_text"]) if "message_text" in msg_row and str(msg_row["message_text"]).lower() != 'nan' else ""
        media_type = msg_row.get("media_type")
        media_id = msg_row.get("media_id")

        # --- STEP 1: Tool Call - Extract Media Transcripts (OCR / ASR) ---
        media_text = self.tools.get_media_transcript(media_type, media_id)
        full_text = raw_text
        if media_text:
            full_text = f"{raw_text} {media_text}".strip()

        # --- STEP 2: Tool Call - Inspect User & Business & Group Profiles ---
        user_profile = self.tools.inspect_user_profile(user_id) if user_id else {}
        group_profile = self.tools.inspect_group_context(group_id, user_id) if group_id else {}
        biz_profile = self.tools.inspect_business_profile(business_id, user_id) if business_id else {}

        # --- STEP 3: Tool Call - Retrieve Historical Evidence & Dismissal History ---
        evidence_res = self.tools.retrieve_historical_evidence(
            user_id, sender_user_id=sender_user_id, business_id=business_id, group_id=group_id, text=full_text
        )
        evidence_ids = evidence_res["evidence_message_ids"]
        has_history_dismissed = evidence_res["has_user_dismissed_or_muted_similar"]

        # --- STEP 4: Tool Call - Safety & Phishing Inspection ---
        is_first_contact = (conv_type == "personal" and sender_user_id and not evidence_ids)
        is_verified_biz = biz_profile.get("verified", False)
        
        safety_res = self.tools.check_safety_and_phishing(
            full_text, is_first_contact=is_first_contact, is_verified_business=is_verified_biz
        )

        if safety_res["is_scam"]:
            evidence_str = ";".join(evidence_ids) if evidence_ids else "none"
            return {
                "message_id": message_id,
                "action": "mute",
                "message_type": safety_res["scam_type"],
                "reason": safety_res["scam_reason"],
                "confidence": 0.85,
                "evidence_message_ids": evidence_str
            }

        if biz_profile.get("domain_risk_detected", False):
            evidence_str = ";".join(evidence_ids) if evidence_ids else "none"
            return {
                "message_id": message_id,
                "action": "mute",
                "message_type": "scam" if "scam" in biz_profile.get("domain_risk_reason", "").lower() else "spam",
                "reason": biz_profile.get("domain_risk_reason"),
                "confidence": 0.88,
                "evidence_message_ids": evidence_str
            }

        # --- STEP 5: Scorer Decision Engine ---
        user_info = self.tools.context_builder.get_user_info(user_id)
        group_info = self.tools.context_builder.get_group_info(group_id)
        member_info = self.tools.context_builder.get_group_member_info(group_id, user_id)
        biz_info = self.tools.context_builder.get_business_info(business_id)
        biz_hist = self.tools.context_builder.get_user_business_history(user_id, business_id)

        action, msg_type, confidence, reason = self.scorer.evaluate_message(
            msg_row, user_info, group_info, member_info, biz_info, biz_hist, full_text, has_history_dismissed=has_history_dismissed
        )

        evidence_str = ";".join(evidence_ids) if evidence_ids else "none"

        return {
            "message_id": message_id,
            "action": action,
            "message_type": msg_type,
            "reason": reason,
            "confidence": round(confidence, 2),
            "evidence_message_ids": evidence_str
        }
