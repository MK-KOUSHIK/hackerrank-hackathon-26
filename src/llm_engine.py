import os
from .schema import PredictionOutputRow, ActionEnum, MessageTypeEnum
from .rules import SafetyRules
from .scorer import Scorer

class LLMEngine:
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir
        self.safety_rules = SafetyRules()
        self.scorer = Scorer()

    def process_message(self, context, content_summary, evidence_ids, has_dismissed_history):
        msg = context.get("message", {})
        msg_id = str(msg.get("message_id"))
        user_id = str(msg.get("user_id")) if msg.get("user_id") else None
        sender_user_id = str(msg.get("sender_user_id")) if msg.get("sender_user_id") else None
        conv_type = str(msg.get("conversation_type", "")).lower()

        biz = context.get("business", {})
        user_biz = context.get("user_business", {})
        group = context.get("group", {})
        member = context.get("group_member", {})
        user_info = context.get("user", {})

        is_verified_biz = bool(biz.get("verified", False))
        is_first_contact = (conv_type == "personal" and sender_user_id and not evidence_ids)

        # 1. Safety Rules Check
        rule_act, rule_type, rule_conf, rule_reason = self.safety_rules.evaluate_rules(
            content_summary, is_first_contact=is_first_contact, is_verified_biz=is_verified_biz, biz_info=biz
        )

        if rule_act is not None:
            evidence_str = ";".join(evidence_ids) if evidence_ids else "none"
            return PredictionOutputRow(
                message_id=msg_id,
                action=rule_act,
                message_type=rule_type,
                reason=rule_reason,
                confidence=rule_conf,
                evidence_message_ids=evidence_str
            )

        # 2. Scorer Reasoning Engine
        act_str, type_str, conf, reason = self.scorer.evaluate_message(
            msg, user_info, group, member, biz, user_biz, content_summary, has_history_dismissed=has_dismissed_history
        )

        evidence_str = ";".join(evidence_ids) if evidence_ids else "none"

        return PredictionOutputRow(
            message_id=msg_id,
            action=ActionEnum(act_str),
            message_type=MessageTypeEnum(type_str),
            reason=reason,
            confidence=conf,
            evidence_message_ids=evidence_str
        )
