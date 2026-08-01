import os
import sys
import pytest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, "code"))
from router.agent_router import AgenticNotificationRouter

def test_personalization_contrast():
    dataset_dir = os.path.join(base_dir, "dataset")
    agent = AgenticNotificationRouter(dataset_dir)
    
    # Message for u_032 (non-dismissing user)
    row_32 = {
        "message_id": "test_32",
        "user_id": "u_032",
        "conversation_type": "group",
        "group_id": "group_005",
        "sender_user_id": "u_048",
        "message_text": "Photos for the kurta set are attached. Pickup is near Gate 2 this weekend.",
        "media_type": "image",
        "media_id": "img_008"
    }
    
    # Message for u_033 (dismissing/muting user)
    row_33 = {
        "message_id": "test_33",
        "user_id": "u_033",
        "conversation_type": "group",
        "group_id": "group_005",
        "sender_user_id": "u_048",
        "message_text": "Photos for the kurta set are attached. Pickup is near Gate 2 this weekend.",
        "media_type": "image",
        "media_id": "img_008"
    }

    res_32 = agent.route_message(row_32)
    res_33 = agent.route_message(row_33)

    # Personalization check: u_032 should be digest, u_033 should be mute!
    assert res_32["action"] == "digest"
    assert res_33["action"] == "mute"
