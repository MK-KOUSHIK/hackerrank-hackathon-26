# Few Shot Solved Examples

```json
[
  {
    "message_id": "sample_msg_001",
    "action": "notify",
    "message_type": "urgent",
    "reason": "A trusted group admin sent a time-sensitive update that should interrupt the user.",
    "confidence": 0.89,
    "evidence_message_ids": "message_0001"
  },
  {
    "message_id": "sample_msg_004",
    "action": "notify",
    "message_type": "business_update",
    "reason": "A verified business is sending an update that matches the user's recent order history.",
    "confidence": 0.91,
    "evidence_message_ids": "message_0004"
  },
  {
    "message_id": "sample_msg_007",
    "action": "digest",
    "message_type": "promotion",
    "reason": "The message is promotional but matches a topic or business the user has opted into.",
    "confidence": 0.78,
    "evidence_message_ids": "message_0007"
  },
  {
    "message_id": "sample_msg_013",
    "action": "mute",
    "message_type": "greeting",
    "reason": "The sender has a pattern of repeated forwards or greetings that the user usually ignores.",
    "confidence": 0.85,
    "evidence_message_ids": "message_0013;message_0014"
  },
  {
    "message_id": "sample_msg_019",
    "action": "mute",
    "message_type": "scam",
    "reason": "The message asks for urgent OTP or account verification through a suspicious flow.",
    "confidence": 0.81,
    "evidence_message_ids": "message_0023"
  }
]
```
