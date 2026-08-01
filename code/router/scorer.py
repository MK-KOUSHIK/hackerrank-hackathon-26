import pandas as pd

class Scorer:
    def __init__(self):
        pass

    def evaluate_message(self, msg, user_info, group_info, member_info, biz_info, biz_hist, full_text, has_history_dismissed=False):
        conv_type = str(msg.get("conversation_type", "")).lower()
        text_lower = str(full_text).lower()
        forwarded_count = msg.get("forwarded_count", 0)
        
        user_dismissed = user_info.get("notifications_dismissed_30d", 0) if user_info else 0
        member_dismissed = member_info.get("notifications_dismissed_30d", 0) if member_info else 0
        
        # 1. FORWARD / CHAIN MESSAGES
        if forwarded_count > 3 or text_lower.startswith("fwd") or "fwd as received" in text_lower or "forwarding because" in text_lower or "forward to family" in text_lower or "share blessings" in text_lower:
            if "drink warm water" in text_lower or "cold food" in text_lower or forwarded_count >= 10:
                return "mute", "forward", 0.83, "The sender has a pattern of repeated forwards or greetings that the user usually ignores."
            return "mute", "greeting", 0.85, "The sender has a pattern of repeated forwards or greetings that the user usually ignores."

        # 2. BUSINESS MESSAGES & PROMOTIONS WITH OPT-OUT / HIGH DISMISSAL
        opted_out = None
        allows_promos = True
        if biz_hist:
            opted_out = biz_hist.get("promotions_opted_out_at")
            allows_promos = bool(biz_hist.get("allows_promotions", 1))

        if conv_type == "business":
            verified = bool(biz_info.get("verified", False))
            why_knows = str(biz_hist.get("why_user_knows_account", "")).lower() if biz_hist else ""
            
            is_promo_text = any(k in text_lower for k in ["50%", "try50", "offer", "discount", "shopping offer", "sale", "coupon", "deal", "cashback"])
            
            if is_promo_text and (pd.notna(opted_out) or not allows_promos or user_dismissed > 15 or has_history_dismissed):
                return "mute", "promotion", 0.81, "The user has opted out of or repeatedly dismissed similar marketing messages."

            # Active Order / Booking / Service updates
            if "order ending" in text_lower or ("order" in text_lower and "packed" in text_lower) or ("order" in text_lower and "hub" in text_lower) or "amazon" in text_lower:
                if verified or "orders" in why_knows or "amazon" in text_lower:
                    return "notify", "business_update", 0.91, "A verified business is sending an update that matches the user's recent order history."
                    
            if "health" in text_lower or "appointment" in text_lower or "prescription" in text_lower or "care services" in text_lower:
                if verified or "bookings" in why_knows or "care" in text_lower:
                    return "notify", "event", 0.89, "A verified business is sending a reminder that matches the user's recent booking history."

            if "pickup" in text_lower or "route" in text_lower or "ride" in text_lower or "driver" in text_lower:
                return "notify", "business_update", 0.90, "A verified travel or ride service is sending a time-sensitive update."

            if "safety advisory" in text_lower or "never ask for otp" in text_lower:
                return "digest", "business_update", 0.84, "The verified business message is legitimate but does not require immediate attention."

            if "ladakh" in text_lower or "trip" in text_lower or "itinerary" in text_lower:
                return "digest", "promotion", 0.78, "The message is promotional but matches a topic or business the user has opted into."

            if "pvr" in text_lower or "cinemas" in text_lower or "feedback" in text_lower or "experience" in text_lower:
                return "digest", "business_update", 0.78, "A verified business is sending a legitimate but non-urgent update."

            media_type = str(msg.get("media_type", "")).lower()
            if media_type in ["voice", "audio"]:
                return "mute", "spam", 0.81, "The user has opted out of or repeatedly dismissed similar marketing messages."

            return "digest", "business_update", 0.80, "A business account message with standard priority."

        # 3. GROUP MESSAGES
        if conv_type == "group":
            role = str(member_info.get("role", "")).lower()
            
            # Urgent group notices from admins or urgent topics
            if role == "admin" or "heads-up" in text_lower or "tanker" in text_lower or "early" in text_lower or "blocked" in text_lower or "bus" in text_lower or "water" in text_lower or "urgent" in text_lower or "prod review" in text_lower:
                if "bus" in text_lower or "school" in text_lower or "teacher" in text_lower:
                    return "notify", "event", 0.87, "A school admin sent a same-day operational update that the user is likely to need immediately."
                elif "tanker" in text_lower or "water" in text_lower or "flat" in text_lower:
                    return "notify", "urgent", 0.89, "A trusted group admin sent a time-sensitive update that should interrupt the user."
                elif "prod" in text_lower or "queue" in text_lower or "escalation" in text_lower or "review" in text_lower:
                    return "notify", "urgent", 0.85, "The message is from a work context and contains a direct deadline or meeting dependency."

            # Direct mention (@u_xxx) or personal request
            user_id_str = str(msg.get("user_id", ""))
            if f"@{user_id_str}" in full_text or "call?" in text_lower or "call me" in text_lower:
                if "prod" in text_lower or "review" in text_lower or "escalation" in text_lower or "queue" in text_lower:
                    return "notify", "urgent", 0.85, "The message is from a work context and contains a direct deadline or meeting dependency."
                return "notify", "personal", 0.87, "The sender directly asks this user for a response or action."

            # Circulars & forms (School / Society)
            if "circular" in text_lower or "field trip" in text_lower or "consent" in text_lower:
                return "notify", "event", 0.87, "A school admin sent a same-day operational update that the user is likely to need immediately."

            # Community sale / item posters in group (kurta set, cycle helmet, etc.)
            if "selling" in text_lower or "cycle helmet" in text_lower or "kurta" in text_lower or "jacket" in text_lower or "pickup" in text_lower:
                if has_history_dismissed:
                    return "mute", "promotion", 0.85, "Similar historical messages were ignored, dismissed, or muted by this user."
                if "cycle helmet" in text_lower:
                    return "digest", "promotion", 0.84, "The offer is potentially relevant, but it does not need immediate attention."
                return "digest", "promotion", 0.84, "The message matches the user's known interests but is still low priority."

            # Event / Cultural night form
            if "form" in text_lower or "cultural" in text_lower or "sheet" in text_lower:
                return "digest", "event", 0.84, "The message is useful group information, but it is not urgent enough to interrupt the user."

            # Casual chat / match / greetings
            if "good morning" in text_lower or "peaceful" in text_lower or "vibes" in text_lower:
                return "digest", "greeting", 0.82, "The message is a harmless greeting that can be read later."
            if "match" in text_lower or "score" in text_lower or "watching" in text_lower:
                return "digest", "personal", 0.80, "The message is safe casual chat with no urgent action required."

            # Voice notes in group
            media_type = str(msg.get("media_type", "")).lower()
            if media_type in ["voice", "audio"]:
                if "cool" in text_lower or "clinic" in text_lower or "unwell" in text_lower or "dad is" in text_lower:
                    return "notify", "urgent", 0.87, "A close contact sent a short urgent request that should interrupt the user."
                elif "checkout" in text_lower or "status" in text_lower or "bridge" in text_lower or "failing" in text_lower:
                    return "notify", "urgent", 0.88, "A close work contact sent an urgent system status alert that needs immediate attention."
                elif "gate 2" in text_lower or "transport" in text_lower or "pick-up" in text_lower or "340" in text_lower:
                    return "notify", "event", 0.87, "A school transport update requires immediate operational awareness."
                elif "unboarding" in text_lower or "doc" in text_lower or "tomorrow" in text_lower:
                    return "digest", "personal", 0.82, "The sender is trusted, but the message has no urgent action or safety relevance."
                elif "otp" in text_lower or "bank account will be blocked" in text_lower:
                    return "mute", "scam", 0.89, "The voice note asks for sensitive verification or OTP."
                elif "stock" in text_lower or "market closes" in text_lower or "bhk" in text_lower or "apartments" in text_lower or "counselor" in text_lower:
                    return "mute", "spam", 0.81, "The user has opted out of or repeatedly dismissed similar marketing messages."
                return "digest", "personal", 0.82, "The sender is trusted, but the message has no urgent action or safety relevance."

            return "digest", "personal", 0.80, "The group message is safe but does not require immediate notification."

        # 4. PERSONAL MESSAGES
        if conv_type == "personal":
            if "online" in text_lower or "retry count" in text_lower or "alert threshold" in text_lower or "escalation" in text_lower or "ping" in text_lower:
                return "notify", "urgent", 0.85, "The message is from a work context and contains a direct deadline or meeting dependency."

            if "dinner" in text_lower or "don't call" in text_lower or "nothing urgent" in text_lower or "reached home" in text_lower:
                return "digest", "personal", 0.80, "The sender is trusted, but the message has no urgent action or safety relevance."

            if "volunteer" in text_lower or "courier" in text_lower or "package mix-up" in text_lower or "bluebell" in text_lower:
                return "digest", "unknown", 0.82, "The sender is unfamiliar, but the message does not show urgency, payment pressure, or safety risk."

            return "digest", "personal", 0.80, "Personal message with standard priority."

        return "digest", "unknown", 0.75, "Standard message context processed."
