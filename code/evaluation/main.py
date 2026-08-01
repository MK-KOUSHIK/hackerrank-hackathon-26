import os
import sys
import pandas as pd

# Add code parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from router.agent_router import AgenticNotificationRouter

def evaluate():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dataset_dir = os.path.join(base_dir, "dataset")
    sample_path = os.path.join(dataset_dir, "sample_messages.csv")
    
    if not os.path.exists(sample_path):
        print(f"Sample messages file not found at {sample_path}")
        return
        
    sample_df = pd.read_csv(sample_path)
    print(f"Evaluating {len(sample_df)} sample messages with Agentic Notification Router...")
    
    agent = AgenticNotificationRouter(dataset_dir)
    
    action_correct = 0
    type_correct = 0
    total = len(sample_df)
    
    results = []
    for _, row in sample_df.iterrows():
        pred = agent.route_message(row.to_dict())
        gt_action = str(row["action"]).strip()
        gt_type = str(row["message_type"]).strip()
        
        act_match = (pred["action"] == gt_action)
        type_match = (pred["message_type"] == gt_type)
        
        if act_match:
            action_correct += 1
        if type_match:
            type_correct += 1
            
        results.append({
            "message_id": row["message_id"],
            "gt_action": gt_action,
            "pred_action": pred["action"],
            "action_match": act_match,
            "gt_type": gt_type,
            "pred_type": pred["message_type"],
            "type_match": type_match,
            "pred_reason": pred["reason"],
            "evidence": pred["evidence_message_ids"]
        })
        
    act_acc = (action_correct / total) * 100
    type_acc = (type_correct / total) * 100
    
    print("\n--- AGENT EVALUATION SUMMARY ---")
    print(f"Action Accuracy: {action_correct}/{total} ({act_acc:.2f}%)")
    print(f"Message Type Accuracy: {type_correct}/{total} ({type_acc:.2f}%)")

if __name__ == "__main__":
    evaluate()
