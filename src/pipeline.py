import os
import sys
import pandas as pd

# Add code directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))
from router.agent_router import AgenticNotificationRouter

class NotificationRouterPipeline:
    def __init__(self, dataset_dir=None):
        if not dataset_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dataset_dir = os.path.join(base_dir, "dataset")
        self.dataset_dir = dataset_dir
        self.agent = AgenticNotificationRouter(self.dataset_dir)

    def process_all(self, in_file=None, out_file=None):
        messages_path = in_file or os.path.join(self.dataset_dir, "messages.csv")
        df = pd.read_csv(messages_path)
        
        results = []
        for _, row in df.iterrows():
            pred = self.agent.route_message(row.to_dict())
            results.append({
                "message_id": pred["message_id"],
                "action": pred["action"],
                "message_type": pred["message_type"],
                "reason": pred["reason"],
                "confidence": pred["confidence"],
                "evidence_message_ids": pred["evidence_message_ids"]
            })
            
        out_df = pd.DataFrame(results)
        if out_file:
            os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
            out_df.to_csv(out_file, index=False)
            
        return out_df
