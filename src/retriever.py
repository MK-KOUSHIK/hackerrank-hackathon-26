import os
import pandas as pd

class EvidenceRetriever:
    def __init__(self, loader):
        self.loader = loader
        self.history_df = loader.message_history_df
        self.events_df = loader.message_events_df

        if not self.history_df.empty and not self.events_df.empty:
            self.merged = pd.merge(self.history_df, self.events_df, on=["user_id", "message_id"], how="left")
        else:
            self.merged = pd.DataFrame()

    def get_evidence(self, user_id, sender_user_id=None, business_id=None, group_id=None, media_id=None, text=""):
        if not user_id:
            return {"evidence_ids": [], "has_dismissed_history": False}

        u_id = str(user_id)
        u_info = self.loader.users.get(u_id, {})
        u_dismissed_30d = u_info.get("notifications_dismissed_30d", 0)

        if self.merged.empty:
            return {"evidence_ids": [], "has_dismissed_history": (u_dismissed_30d > 10)}

        user_history = self.merged[self.merged["user_id"] == u_id]

        if user_history.empty:
            return {"evidence_ids": [], "has_dismissed_history": (u_dismissed_30d > 10)}

        text_lower = str(text).lower() if text else ""
        m_id = str(media_id) if pd.notna(media_id) else None
        s_id = str(sender_user_id) if pd.notna(sender_user_id) else None
        b_id = str(business_id) if pd.notna(business_id) else None
        g_id = str(group_id) if pd.notna(group_id) else None

        matches = []
        dismissed_count = 0

        for _, rec in user_history.iterrows():
            rec_m = str(rec.get("media_id")) if pd.notna(rec.get("media_id")) else None
            rec_s = str(rec.get("sender_user_id")) if pd.notna(rec.get("sender_user_id")) else None
            rec_b = str(rec.get("business_id")) if pd.notna(rec.get("business_id")) else None
            rec_g = str(rec.get("group_id")) if pd.notna(rec.get("group_id")) else None
            rec_text = str(rec.get("message_text", "")).lower() if pd.notna(rec.get("message_text")) else ""

            is_match = False
            if m_id and rec_m == m_id:
                is_match = True
            elif b_id and rec_b == b_id:
                is_match = True
            elif s_id and rec_s == s_id:
                is_match = True
            elif g_id and rec_g == g_id and s_id and rec_s == s_id:
                is_match = True
            elif text_lower and rec_text:
                if any(kw in text_lower for kw in ["forward", "fwd", "otp", "kurta", "helmet", "50%"]):
                    if any(kw in rec_text for kw in ["forward", "fwd", "otp", "kurta", "helmet", "50%"]):
                        is_match = True

            if is_match:
                matches.append(str(rec["message_id"]))

            if rec.get("notification_dismissed") == 1 or rec.get("muted_after_message") == 1:
                dismissed_count += 1

        total_user_hist = len(user_history)
        has_dismissed_history = (total_user_hist > 0 and (dismissed_count / total_user_hist) >= 0.5) or (u_dismissed_30d > 10)
        return {
            "evidence_ids": matches[:2],
            "has_dismissed_history": has_dismissed_history
        }
