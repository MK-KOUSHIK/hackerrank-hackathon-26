import argparse
import os
import sys
import pandas as pd

# Add code directory to path for modular import
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "code"))
from router.agent_router import AgenticNotificationRouter

def main():
    parser = argparse.ArgumentParser(description="WhatsApp Message Notification Router CLI")
    parser.add_argument("--in", dest="in_file", default="dataset/messages.csv", help="Input messages CSV file")
    parser.add_argument("--out", dest="out_file", default="dataset/output.csv", help="Output predictions CSV file")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "dataset")

    print("=== WhatsApp Message Notification Router ===")
    print(f"Input file:  {args.in_file}")
    print(f"Output file: {args.out_file}")
    print(f"Dataset dir: {dataset_dir}")

    if not os.path.exists(args.in_file):
        print(f"Error: Input file not found at {args.in_file}")
        sys.exit(1)

    messages_df = pd.read_csv(args.in_file)
    print(f"Loaded {len(messages_df)} incoming messages to route.")

    agent = AgenticNotificationRouter(dataset_dir)
    output_rows = []

    for _, row in messages_df.iterrows():
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

    os.makedirs(os.path.dirname(os.path.abspath(args.out_file)), exist_ok=True)
    output_df.to_csv(args.out_file, index=False)

    # Save to root output.csv as well if target is dataset/output.csv
    root_output_path = os.path.join(base_dir, "output.csv")
    output_df.to_csv(root_output_path, index=False)

    print(f"\nPipeline complete! Produced {len(output_df)} predictions.")
    print("\nAction Breakdown:")
    print(output_df["action"].value_counts())
    print("\nMessage Type Breakdown:")
    print(output_df["message_type"].value_counts())

if __name__ == "__main__":
    main()
