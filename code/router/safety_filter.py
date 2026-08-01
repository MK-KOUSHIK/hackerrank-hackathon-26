import re

class SafetyFilter:
    def __init__(self):
        # Adversarial prompt injection signatures
        self.injection_patterns = [
            r"ignore (all )?previous (routing )?rules",
            r"mark this message as",
            r"instruct the router",
            r"override routing",
            r"system prompt:",
            r"actual message:"
        ]
        
        # Scam & phishing credential theft keywords
        self.scam_keywords = [
            r"\botp\b",
            r"6 digit (login )?code",
            r"password",
            r"verify (now|immediately)",
            r"account (may be|will be) (temporarily )?blocked",
            r"profile will be blocked",
            r"wallet verification failed",
            r"account access will expire",
            r"bank account will be blocked",
            r"scan this qr and pay",
            r"penalty list"
        ]

    def check_prompt_injection(self, text):
        text_lower = text.lower()
        for pattern in self.injection_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def check_scam_phishing(self, text, is_first_contact=False, is_verified_business=False):
        text_lower = text.lower()
        
        # Prompt injection check
        if self.check_prompt_injection(text):
            return True, "scam", "The message tries to instruct the router, but the routing decision should be based on the actual content and risk."

        # Safety advisories explicitly saying "never ask for OTP" from verified business are NOT scams!
        if is_verified_business and ("never ask for otp" in text_lower or "safety advisory" in text_lower):
            return False, None, None

        # Phishing credential/payment pressure checks
        scam_hit = False
        for pattern in self.scam_keywords:
            if re.search(pattern, text_lower):
                scam_hit = True
                break

        if scam_hit:
            if is_first_contact:
                return True, "scam", "This is the first message from the sender and it asks for sensitive verification or payment."
            elif "otp" in text_lower or "code" in text_lower:
                return True, "scam", "The message asks for urgent OTP or account verification through a suspicious flow."
            elif "blocked" in text_lower or "expire" in text_lower:
                return True, "scam", "The message uses fake support language and account-blocking pressure to push the user into action."
            else:
                return True, "scam", "The message demands urgent payment or security verification via suspicious links."

        return False, None, None

    def check_business_domain_risk(self, biz_info):
        if not biz_info:
            return False, None, None

        verified = bool(biz_info.get("verified", False))
        official = str(biz_info.get("official_domain", "")).lower() if pd_not_na(biz_info.get("official_domain")) else ""
        sender_dom = str(biz_info.get("domain_used_by_sender", "")).lower() if pd_not_na(biz_info.get("domain_used_by_sender")) else ""
        dom_age = biz_info.get("domain_used_by_sender_age_days", 999)
        reports = biz_info.get("user_reports_30d", 0)

        # Allow standard shortener domains for verified businesses
        known_shorteners = ["wame.pro", "link.wame.pro", "wa.me", "bit.ly", "tinyurl.com"]
        if verified and any(s in sender_dom for s in known_shorteners):
            return False, None, None

        if not verified and (dom_age < 30 or reports > 10):
            if reports > 15:
                return True, "spam", "The user has opted out of or repeatedly dismissed similar marketing messages."
            return True, "scam", "The sender domain is recently registered and has received user scam/spam reports."

        if not verified and official and sender_dom and official != sender_dom:
            return True, "scam", "The sender domain does not match the official business domain."

        return False, None, None

def pd_not_na(val):
    return val is not None and str(val).lower() != 'nan' and str(val).lower() != 'none'
