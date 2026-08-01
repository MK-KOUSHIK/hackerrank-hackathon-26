import os
import sys
import pandas as pd

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from router.agent_router import AgenticNotificationRouter

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, "dataset")
    messages_path = os.path.join(dataset_dir, "messages.csv")
    
    if not os.path.exists(messages_path):
        print(f"Error: messages.csv not found at {messages_path}")
        sys.exit(1)
        
    print(f"Loading incoming messages from {messages_path}...")
    messages_df = pd.read_csv(messages_path)
    total_messages = len(messages_df)
    print(f"Total incoming messages to route: {total_messages}")
    
    print("Initializing Agentic Notification Router...")
    agent = AgenticNotificationRouter(dataset_dir)
    
    output_rows = []
    print("Running autonomous agent routing loop...")
    for idx, row in messages_df.iterrows():
        pred = agent.route_message(row.to_dict())
        output_rows.append({
            "message_id": pred["message_id"],
            "action": pred["action"],
            "message_type": pred["message_type"],
            "reason": pred["reason"],
            "confidence": pred["confidence"],
            "evidence_message_ids": pred["evidence_message_ids"]
        })
        
    output_df = pd.DataFrame(output_rows)
    
    # Save output to dataset/output.csv and root output.csv
    dataset_output_path = os.path.join(dataset_dir, "output.csv")
    root_output_path = os.path.join(base_dir, "output.csv")
    
    output_df.to_csv(dataset_output_path, index=False)
    output_df.to_csv(root_output_path, index=False)
    
    print(f"\nAgent routing complete! Saved {len(output_df)} predictions to:")
    print(f"1. {dataset_output_path}")
    print(f"2. {root_output_path}")
    print("\nAction Breakdown:")
    print(output_df["action"].value_counts())
    print("\nMessage Type Breakdown:")
    print(output_df["message_type"].value_counts())

if __name__ == "__main__":
    main()
