from .context_builder import ContextBuilder
from .media_processor import MediaProcessor
from .safety_filter import SafetyFilter
from .scorer import Scorer

class RouterPipeline:
    def __init__(self, dataset_dir):
        self.context_builder = ContextBuilder(dataset_dir)
        self.media_processor = MediaProcessor(dataset_dir)
        self.safety_filter = SafetyFilter()
        self.scorer = Scorer()

    def route_message(self, msg_row):
        message_id = str(msg_row["message_id"])
        user_id = str(msg_row["user_id"]) if "user_id" in msg_row and msg_row["user_id"] else None
        conversation_type = str(msg_row["conversation_type"]) if "conversation_type" in msg_row else ""
        group_id = str(msg_row["group_id"]) if "group_id" in msg_row and msg_row["group_id"] else None
        business_id = str(msg_row["business_id"]) if "business_id" in msg_row and msg_row["business_id"] else None
        sender_user_id = str(msg_row["sender_user_id"]) if "sender_user_id" in msg_row and msg_row["sender_user_id"] else None
        
        raw_text = str(msg_row["message_text"]) if "message_text" in msg_row and str(msg_row["message_text"]).lower() != 'nan' else ""
        media_type = msg_row.get("media_type")
        media_id = msg_row.get("media_id")
        
        # 1. Fetch Media Text (OCR / ASR transcript)
        media_text = self.media_processor.get_media_text(media_type, media_id)
        
        # Combine text content
        full_text = raw_text
        if media_text:
            full_text = f"{raw_text} {media_text}".strip()
            
        # 2. Lookup Context Info
        user_info = self.context_builder.get_user_info(user_id)
        group_info = self.context_builder.get_group_info(group_id)
        member_info = self.context_builder.get_group_member_info(group_id, user_id)
        biz_info = self.context_builder.get_business_info(business_id)
        biz_hist = self.context_builder.get_user_business_history(user_id, business_id)
        
        is_verified_biz = bool(biz_info.get("verified", False))
        
        # Check historical dismissal/mute preference for user
        has_history_dismissed = self.context_builder.check_user_historical_dismissal(user_id, media_id, full_text)
        
        # 3. Safety & Phishing Pre-Filter
        is_first_contact = False
        if conversation_type == "personal" and sender_user_id:
            hist_matches = self.context_builder.get_matching_historical_evidence(user_id, sender_user_id=sender_user_id)
            if not hist_matches:
                is_first_contact = True
                
        is_scam, scam_type, scam_reason = self.safety_filter.check_scam_phishing(
            full_text, is_first_contact=is_first_contact, is_verified_business=is_verified_biz
        )
        if is_scam:
            evidence_ids = self.context_builder.get_matching_historical_evidence(user_id, sender_user_id, business_id, group_id, full_text)
            evidence_str = ";".join(evidence_ids[:2]) if evidence_ids else "none"
            return {
                "message_id": message_id,
                "action": "mute",
                "message_type": scam_type,
                "reason": scam_reason,
                "confidence": 0.85,
                "evidence_message_ids": evidence_str
            }
            
        is_domain_risk, dom_type, dom_reason = self.safety_filter.check_business_domain_risk(biz_info)
        if is_domain_risk:
            evidence_ids = self.context_builder.get_matching_historical_evidence(user_id, business_id=business_id)
            evidence_str = ";".join(evidence_ids[:2]) if evidence_ids else "none"
            return {
                "message_id": message_id,
                "action": "mute",
                "message_type": dom_type,
                "reason": dom_reason,
                "confidence": 0.88,
                "evidence_message_ids": evidence_str
            }

        # 4. Scorer Evaluation
        action, msg_type, confidence, reason = self.scorer.evaluate_message(
            msg_row, user_info, group_info, member_info, biz_info, biz_hist, full_text, has_history_dismissed=has_history_dismissed
        )
        
        # 5. Gather Historical Evidence IDs
        evidence_ids = self.context_builder.get_matching_historical_evidence(
            user_id, sender_user_id, business_id, group_id, full_text
        )
        evidence_str = ";".join(evidence_ids[:2]) if evidence_ids else "none"
        
        return {
            "message_id": message_id,
            "action": action,
            "message_type": msg_type,
            "reason": reason,
            "confidence": round(confidence, 2),
            "evidence_message_ids": evidence_str
        }
