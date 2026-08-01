import os
import json

class MultimodalNormalizer:
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir
        self.cache_dir = os.path.join(dataset_dir, "processed_media")
        
        self.ocr_cache = {}
        self.audio_cache = {}
        
        ocr_p = os.path.join(self.cache_dir, "ocr_transcripts.json")
        if os.path.exists(ocr_p):
            with open(ocr_p, "r", encoding="utf-8") as f:
                self.ocr_cache = json.load(f)
                
        audio_p = os.path.join(self.cache_dir, "audio_transcripts.json")
        if os.path.exists(audio_p):
            with open(audio_p, "r", encoding="utf-8") as f:
                self.audio_cache = json.load(f)

    def normalize_message(self, msg):
        raw_text = str(msg.get("message_text", "")) if pd_not_na(msg.get("message_text")) else ""
        media_type = str(msg.get("media_type", "")).lower() if pd_not_na(msg.get("media_type")) else ""
        media_id = str(msg.get("media_id", "")).strip() if pd_not_na(msg.get("media_id")) else ""
        
        media_text = ""
        low_confidence_media = False
        
        if media_type == "image" and media_id:
            media_text = self.ocr_cache.get(media_id, "")
            if not media_text:
                low_confidence_media = True
        elif media_type in ["voice", "audio"] and media_id:
            media_text = self.audio_cache.get(media_id, "")
            if not media_text:
                low_confidence_media = True
                
        content_summary = f"{raw_text} {media_text}".strip()
        return {
            "raw_text": raw_text,
            "media_text": media_text,
            "content_summary": content_summary,
            "low_confidence_media": low_confidence_media
        }

def pd_not_na(val):
    return val is not None and str(val).lower() != 'nan' and str(val).lower() != 'none'
