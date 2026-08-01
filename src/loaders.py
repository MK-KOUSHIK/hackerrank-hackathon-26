import os
import pandas as pd

def resolve_dataset_dir(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, "dataset")
    if not os.path.exists(dataset_dir):
        raise FileNotFoundError(f"Dataset directory not found at {dataset_dir}")
    return dataset_dir

class DataLoader:
    def __init__(self, dataset_dir=None):
        self.dataset_dir = dataset_dir or resolve_dataset_dir()
        
        self.users_df = self._read("users.csv")
        self.groups_df = self._read("groups.csv")
        self.group_members_df = self._read("group_members.csv")
        self.business_df = self._read("business_accounts.csv")
        self.user_business_df = self._read("user_business_history.csv")
        self.message_history_df = self._read("message_history.csv")
        self.message_events_df = self._read("message_events.csv")
        self.messages_df = self._read("messages.csv")
        
        # Build lookup tables
        self.users = self.users_df.set_index("user_id").to_dict("index") if not self.users_df.empty else {}
        self.groups = self.groups_df.set_index("group_id").to_dict("index") if not self.groups_df.empty else {}
        self.business = self.business_df.set_index("business_id").to_dict("index") if not self.business_df.empty else {}

        self.group_members = {}
        if not self.group_members_df.empty:
            for _, r in self.group_members_df.iterrows():
                self.group_members[(str(r["group_id"]), str(r["user_id"]))] = r.to_dict()

        self.user_business = {}
        if not self.user_business_df.empty:
            for _, r in self.user_business_df.iterrows():
                self.user_business[(str(r["user_id"]), str(r["business_id"]))] = r.to_dict()

    def _read(self, fname):
        p = os.path.join(self.dataset_dir, fname)
        return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()

    def build_context(self, msg_id):
        msg_rows = self.messages_df[self.messages_df["message_id"] == msg_id]
        if msg_rows.empty:
            return {}
        msg = msg_rows.iloc[0].to_dict()
        u_id = str(msg.get("user_id")) if pd.notna(msg.get("user_id")) else None
        g_id = str(msg.get("group_id")) if pd.notna(msg.get("group_id")) else None
        b_id = str(msg.get("business_id")) if pd.notna(msg.get("business_id")) else None

        return {
            "message": msg,
            "user": self.users.get(u_id, {}),
            "group": self.groups.get(g_id, {}),
            "group_member": self.group_members.get((g_id, u_id), {}),
            "business": self.business.get(b_id, {}),
            "user_business": self.user_business.get((u_id, b_id), {})
        }
