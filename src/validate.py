import argparse
import os
import sys
import pandas as pd
from .schema import ActionEnum, MessageTypeEnum

def validate_output(output_path, expected_messages_path=None):
    print(f"Validating predictions file: {output_path}")
    if not os.path.exists(output_path):
        print(f"ERROR: Output file does not exist: {output_path}")
        return False

    df = pd.read_csv(output_path)
    
    # 1. Required columns check
    req_cols = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
    if list(df.columns) != req_cols:
        print(f"ERROR: Column mismatch! Expected {req_cols}, got {list(df.columns)}")
        return False

    # 2. Row count check if expected_messages_path provided
    if expected_messages_path and os.path.exists(expected_messages_path):
        msg_df = pd.read_csv(expected_messages_path)
        if len(df) != len(msg_df):
            print(f"ERROR: Row count mismatch! Expected {len(msg_df)} rows, got {len(df)}")
            return False
            
    # 3. Enum validation
    allowed_actions = {e.value for e in ActionEnum}
    allowed_types = {e.value for e in MessageTypeEnum}

    invalid_actions = set(df["action"]) - allowed_actions
    if invalid_actions:
        print(f"ERROR: Invalid action values found: {invalid_actions}")
        return False

    invalid_types = set(df["message_type"]) - allowed_types
    if invalid_types:
        print(f"ERROR: Invalid message_type values found: {invalid_types}")
        return False

    # 4. Null values check
    if df.isna().sum().sum() > 0:
        print(f"ERROR: Found null values in output:\n{df.isna().sum()}")
        return False

    # 5. Confidence range check
    if (df["confidence"] < 0.0).any() or (df["confidence"] > 1.0).any():
        print("ERROR: Confidence out of range [0.0, 1.0]")
        return False

    print("SUCCESS: Output file passed all validation checks cleanly!")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="dataset/output.csv")
    parser.add_argument("--in", dest="in_file", default="dataset/messages.csv")
    args = parser.parse_args()
    
    valid = validate_output(args.out, args.in_file)
    if not valid:
        sys.exit(1)

if __name__ == "__main__":
    main()
