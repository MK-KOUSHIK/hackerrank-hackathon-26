import re
from .schema import ActionEnum, MessageTypeEnum

class SafetyRules:
    def __init__(self):
        self.injection_patterns = [
            r"ignore (all )?previous (routing )?rules",
            r"mark this message as",
            r"instruct the router",
            r"override routing",
            r"system prompt:"
        ]
        self.scam_patterns = [
            r"\botp\b",
            r"6 digit (login )?code",
            r"password",
            r"verify (now|immediately)",
            r"account (may be|will be) (temporarily )?blocked",
            r"profile will be blocked",
            r"wallet verification failed",
            r"account access will expire",
            r"bank account will be blocked",
            r"scan this qr and pay"
        ]

    def evaluate_rules(self, text, is_first_contact=False, is_verified_biz=False, biz_info=None):
        text_lower = text.lower() if text else ""

        # 1. Prompt Injection
        for pat in self.injection_patterns:
            if re.search(pat, text_lower):
                return ActionEnum.MUTE, MessageTypeEnum.SCAM, 0.85, "The message tries to instruct the router, but the routing decision should be based on the actual content and risk."

        # 2. Safety advisory exception for verified business
        if is_verified_biz and ("never ask for otp" in text_lower or "safety advisory" in text_lower):
            return None, None, None, None

        # 3. Phishing / Scam
        for pat in self.scam_patterns:
            if re.search(pat, text_lower):
                if is_first_contact:
                    return ActionEnum.MUTE, MessageTypeEnum.SCAM, 0.87, "This is the first message from the sender and it asks for sensitive verification or payment."
                elif "otp" in text_lower or "code" in text_lower:
                    return ActionEnum.MUTE, MessageTypeEnum.SCAM, 0.85, "The message asks for urgent OTP or account verification through a suspicious flow."
                elif "blocked" in text_lower or "expire" in text_lower:
                    return ActionEnum.MUTE, MessageTypeEnum.SCAM, 0.87, "The message uses fake support language and account-blocking pressure to push the user into action."
                return ActionEnum.MUTE, MessageTypeEnum.SCAM, 0.85, "The message demands urgent payment or security verification via suspicious links."

        # 4. Business Domain Risk
        if biz_info:
            official = str(biz_info.get("official_domain", "")).lower()
            sender_dom = str(biz_info.get("domain_used_by_sender", "")).lower()
            verified = bool(biz_info.get("verified", False))
            dom_age = biz_info.get("domain_used_by_sender_age_days", 999)
            reports = biz_info.get("user_reports_30d", 0)

            shorteners = ["wame.pro", "link.wame.pro", "wa.me", "bit.ly"]
            if not verified and (dom_age < 30 or reports > 10):
                if reports > 15:
                    return ActionEnum.MUTE, MessageTypeEnum.SPAM, 0.81, "The user has opted out of or repeatedly dismissed similar marketing messages."
                return ActionEnum.MUTE, MessageTypeEnum.SCAM, 0.88, "The sender domain is recently registered and has received user scam/spam reports."

            if not verified and official and sender_dom and official != sender_dom and not any(s in sender_dom for s in shorteners):
                return ActionEnum.MUTE, MessageTypeEnum.SCAM, 0.88, "The sender domain does not match the official business domain."

        return None, None, None, None
