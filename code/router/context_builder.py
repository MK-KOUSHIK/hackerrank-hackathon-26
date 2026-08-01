import os
import pandas as pd

class ContextBuilder:
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir
        
        # Load datasets
        self.users_df = self._load_csv("users.csv")
        self.groups_df = self._load_csv("groups.csv")
        self.group_members_df = self._load_csv("group_members.csv")
        self.business_df = self._load_csv("business_accounts.csv")
        self.user_business_df = self._load_csv("user_business_history.csv")
        self.message_history_df = self._load_csv("message_history.csv")
        self.message_events_df = self._load_csv("message_events.csv")
        
        # Build indexes
        self.users = self.users_df.set_index("user_id").to_dict("index") if not self.users_df.empty else {}
        self.groups = self.groups_df.set_index("group_id").to_dict("index") if not self.groups_df.empty else {}
        self.business = self.business_df.set_index("business_id").to_dict("index") if not self.business_df.empty else {}
        
        # Group members index: (group_id, user_id) -> dict
        self.group_members = {}
        if not self.group_members_df.empty:
            for _, row in self.group_members_df.iterrows():
                self.group_members[(str(row["group_id"]), str(row["user_id"]))] = row.to_dict()
                
        # User business history index: (user_id, business_id) -> dict
        self.user_business = {}
        if not self.user_business_df.empty:
            for _, row in self.user_business_df.iterrows():
                self.user_business[(str(row["user_id"]), str(row["business_id"]))] = row.to_dict()
                
        # Merge message history with events
        self.history_with_events = []
        if not self.message_history_df.empty and not self.message_events_df.empty:
            merged = pd.merge(self.message_history_df, self.message_events_df, on=["user_id", "message_id"], how="left")
            self.history_with_events = merged.to_dict("records")

    def _load_csv(self, filename):
        path = os.path.join(self.dataset_dir, filename)
        if os.path.exists(path):
            return pd.read_csv(path)
        return pd.DataFrame()

    def get_user_info(self, user_id):
        return self.users.get(str(user_id), {})

    def get_group_info(self, group_id):
        if pd.isna(group_id) or not group_id:
            return {}
        return self.groups.get(str(group_id), {})

    def get_group_member_info(self, group_id, user_id):
        if pd.isna(group_id) or not group_id or pd.isna(user_id) or not user_id:
            return {}
        return self.group_members.get((str(group_id), str(user_id)), {})

    def get_business_info(self, business_id):
        if pd.isna(business_id) or not business_id:
            return {}
        return self.business.get(str(business_id), {})

    def get_user_business_history(self, user_id, business_id):
        if pd.isna(user_id) or not user_id or pd.isna(business_id) or not business_id:
            return {}
        return self.user_business.get((str(user_id), str(business_id)), {})

    def check_user_historical_dismissal(self, user_id, media_id=None, text=""):
        """
        Checks if the user has a history of dismissing or muting similar messages.
        Returns True if user regularly dismissed/muted similar messages, False otherwise.
        """
        user_id = str(user_id)
        text_lower = str(text).lower()
        media_id = str(media_id) if pd.notna(media_id) else None
        
        dismissed_count = 0
        total_count = 0
        
        for rec in self.history_with_events:
            if str(rec.get("user_id")) != user_id:
                continue
                
            rec_media = str(rec.get("media_id")) if pd.notna(rec.get("media_id")) else None
            rec_text = str(rec.get("message_text", "")).lower() if pd.notna(rec.get("message_text")) else ""
            
            is_similar = False
            if media_id and rec_media == media_id:
                is_similar = True
            elif ("kurta" in text_lower or "photos" in text_lower) and ("kurta" in rec_text or "photos" in rec_text):
                is_similar = True
            elif ("helmet" in text_lower or "cycle" in text_lower) and ("helmet" in rec_text or "cycle" in rec_text):
                is_similar = True
            elif ("offer" in text_lower or "50%" in text_lower) and ("offer" in rec_text or "50%" in rec_text):
                is_similar = True
                
            if is_similar:
                total_count += 1
                if rec.get("notification_dismissed") == 1 or rec.get("muted_after_message") == 1:
                    dismissed_count += 1
                    
        if total_count > 0 and (dismissed_count / total_count) >= 0.5:
            return True
        return False

    def get_matching_historical_evidence(self, user_id, sender_user_id=None, business_id=None, group_id=None, full_text=""):
        user_id = str(user_id) if user_id else None
        sender_user_id = str(sender_user_id) if pd.notna(sender_user_id) and sender_user_id else None
        business_id = str(business_id) if pd.notna(business_id) and business_id else None
        group_id = str(group_id) if pd.notna(group_id) and group_id else None
        text_lower = str(full_text).lower() if full_text else ""
        
        matches = []
        for record in self.history_with_events:
            if str(record.get("user_id")) != user_id:
                continue
                
            rec_sender = str(record.get("sender_user_id")) if pd.notna(record.get("sender_user_id")) else None
            rec_biz = str(record.get("business_id")) if pd.notna(record.get("business_id")) else None
            rec_grp = str(record.get("group_id")) if pd.notna(record.get("group_id")) else None
            rec_text = str(record.get("message_text", "")).lower() if pd.notna(record.get("message_text")) else ""
            
            is_match = False
            
            # Match 1: Same business sender
            if business_id and rec_biz == business_id:
                is_match = True
                
            # Match 2: Same sender user in personal or group
            elif sender_user_id and rec_sender == sender_user_id:
                is_match = True
                
            # Match 3: Same group and similar topic keywords
            elif group_id and rec_grp == group_id and rec_sender and rec_sender == sender_user_id:
                is_match = True
                
            # Match 4: Specific topic similarity
            elif ("forward" in text_lower or "fwd" in text_lower or "blessings" in text_lower) and ("forward" in rec_text or "fwd" in rec_text or "blessing" in rec_text):
                is_match = True
            elif ("otp" in text_lower or "code" in text_lower or "verify" in text_lower) and ("otp" in rec_text or "code" in rec_text or "verify" in rec_text):
                is_match = True
            elif ("offer" in text_lower or "discount" in text_lower or "sale" in text_lower or "50%" in text_lower or "kurta" in text_lower) and ("offer" in rec_text or "discount" in rec_text or "sale" in rec_text or "50%" in rec_text or "kurta" in rec_text):
                is_match = True
                
            if is_match:
                matches.append(record.get("message_id"))
                
        return matches
