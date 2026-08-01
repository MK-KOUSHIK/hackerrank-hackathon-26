import os
import json

class MediaProcessor:
    def __init__(self, dataset_dir):
        self.dataset_dir = dataset_dir
        self.processed_dir = os.path.join(dataset_dir, "processed_media")
        
        self.ocr_transcripts = {}
        self.audio_transcripts = {}
        
        ocr_path = os.path.join(self.processed_dir, "ocr_transcripts.json")
        if os.path.exists(ocr_path):
            with open(ocr_path, "r", encoding="utf-8") as f:
                self.ocr_transcripts = json.load(f)
                
        audio_path = os.path.join(self.processed_dir, "audio_transcripts.json")
        if os.path.exists(audio_path):
            with open(audio_path, "r", encoding="utf-8") as f:
                self.audio_transcripts = json.load(f)
                
    def get_media_text(self, media_type, media_id):
        if not media_type or str(media_type).lower() == 'nan' or not media_id or str(media_id).lower() == 'nan':
            return ""
            
        media_type = str(media_type).strip().lower()
        media_id = str(media_id).strip()
        
        if media_type == 'image':
            return self.ocr_transcripts.get(media_id, "")
        elif media_type == 'voice' or media_type == 'audio':
            return self.audio_transcripts.get(media_id, "")
        return ""
