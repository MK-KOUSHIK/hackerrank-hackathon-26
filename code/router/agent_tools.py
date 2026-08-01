from .context_builder import ContextBuilder
from .media_processor import MediaProcessor
from .safety_filter import SafetyFilter

class RouterTools:
    def __init__(self, dataset_dir):
        self.context_builder = ContextBuilder(dataset_dir)
        self.media_processor = MediaProcessor(dataset_dir)
        self.safety_filter = SafetyFilter()

    def inspect_user_profile(self, user_id):
        """Returns user notification stats, quiet hours, and dismissal history."""
        user_info = self.context_builder.get_user_info(user_id)
        return {
            "user_id": user_id,
            "dnd_window": user_info.get("do_not_disturb_window", None),
            "messages_opened_30d": user_info.get("messages_opened_30d", 0),
            "messages_replied_30d": user_info.get("messages_replied_30d", 0),
            "notifications_dismissed_30d": user_info.get("notifications_dismissed_30d", 0),
            "messages_reported_30d": user_info.get("messages_reported_30d", 0)
        }

    def inspect_group_context(self, group_id, user_id):
        """Returns group type, member count, user role, and user mute preference."""
        group_info = self.context_builder.get_group_info(group_id)
        member_info = self.context_builder.get_group_member_info(group_id, user_id)
        return {
            "group_id": group_id,
            "group_name": group_info.get("group_name", None),
            "group_type": group_info.get("group_type", None),
            "member_count": group_info.get("member_count", 0),
            "admin_count": group_info.get("admin_count", 0),
            "user_role": member_info.get("role", "member"),
            "group_muted_by_user": bool(member_info.get("group_muted_by_user", False)),
            "notifications_dismissed_30d": member_info.get("notifications_dismissed_30d", 0)
        }

    def inspect_business_profile(self, business_id, user_id):
        """Returns business verification, domain match, and user opt-in/opt-out status."""
        biz_info = self.context_builder.get_business_info(business_id)
        biz_hist = self.context_builder.get_user_business_history(user_id, business_id)
        
        domain_risk, risk_type, risk_reason = self.safety_filter.check_business_domain_risk(biz_info)
        
        return {
            "business_id": business_id,
            "display_name": biz_info.get("display_name", None),
            "category": biz_info.get("category", None),
            "verified": bool(biz_info.get("verified", False)),
            "official_domain": biz_info.get("official_domain", None),
            "domain_used_by_sender": biz_info.get("domain_used_by_sender", None),
            "domain_risk_detected": domain_risk,
            "domain_risk_reason": risk_reason,
            "user_relationship": biz_hist.get("why_user_knows_account", None) if biz_hist else None,
            "allows_promotions": bool(biz_hist.get("allows_promotions", True)) if biz_hist else True,
            "promotions_opted_out_at": biz_hist.get("promotions_opted_out_at", None) if biz_hist else None
        }

    def get_media_transcript(self, media_type, media_id):
        """Extracts OCR text from images or ASR transcript from voice notes."""
        return self.media_processor.get_media_text(media_type, media_id)

    def retrieve_historical_evidence(self, user_id, sender_user_id=None, business_id=None, group_id=None, text=""):
        """Queries past messages to retrieve evidence message IDs and user reaction history."""
        evidence_ids = self.context_builder.get_matching_historical_evidence(
            user_id, sender_user_id, business_id, group_id, text
        )
        has_dismissed_history = self.context_builder.check_user_historical_dismissal(user_id, text=text)
        return {
            "evidence_message_ids": evidence_ids[:2] if evidence_ids else [],
            "has_user_dismissed_or_muted_similar": has_dismissed_history
        }

    def check_safety_and_phishing(self, text, is_first_contact=False, is_verified_business=False):
        """Checks for adversarial prompt injections, OTP phishing, and scam alerts."""
        is_scam, scam_type, scam_reason = self.safety_filter.check_scam_phishing(
            text, is_first_contact=is_first_contact, is_verified_business=is_verified_business
        )
        return {
            "is_scam": is_scam,
            "scam_type": scam_type,
            "scam_reason": scam_reason
        }
