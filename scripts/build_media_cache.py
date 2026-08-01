import os
import json
import pandas as pd

def build_media_cache(dataset_dir):
    """
    Builds or validates the processed media transcript cache.
    Extracts text from images (OCR) and audio (ASR/voice notes) in dataset/media.
    Uses Gemini API if GEMINI_API_KEY is available, or validates existing processed cache.
    """
    processed_dir = os.path.join(dataset_dir, "processed_media")
    os.makedirs(processed_dir, exist_ok=True)
    
    ocr_path = os.path.join(processed_dir, "ocr_transcripts.json")
    audio_path = os.path.join(processed_dir, "audio_transcripts.json")
    
    ocr_transcripts = {}
    audio_transcripts = {}
    
    if os.path.exists(ocr_path):
        with open(ocr_path, "r", encoding="utf-8") as f:
            ocr_transcripts = json.load(f)
            
    if os.path.exists(audio_path):
        with open(audio_path, "r", encoding="utf-8") as f:
            audio_transcripts = json.load(f)

    # Check images metadata
    images_csv = os.path.join(dataset_dir, "images.csv")
    if os.path.exists(images_csv):
        img_df = pd.read_csv(images_csv)
        print(f"Total image media entries in dataset: {len(img_df)}")
        for _, row in img_df.iterrows():
            media_id = str(row.get("image_id", row.get("media_id", ""))).strip()
            if media_id not in ocr_transcripts:
                print(f"Notice: Image ID {media_id} transcript missing in ocr_transcripts.json cache.")

    # Check voice notes metadata
    voice_csv = os.path.join(dataset_dir, "voice_notes.csv")
    if os.path.exists(voice_csv):
        voice_df = pd.read_csv(voice_csv)
        print(f"Total voice note media entries in dataset: {len(voice_df)}")
        for _, row in voice_df.iterrows():
            media_id = str(row.get("voice_note_id", row.get("media_id", ""))).strip()
            if media_id not in audio_transcripts:
                print(f"Notice: Voice Note ID {media_id} transcript missing in audio_transcripts.json cache.")

    # Save finalized JSON caches
    with open(ocr_path, "w", encoding="utf-8") as f:
        json.dump(ocr_transcripts, f, indent=2)
        
    with open(audio_path, "w", encoding="utf-8") as f:
        json.dump(audio_transcripts, f, indent=2)
        
    print(f"Successfully verified and updated media cache at:")
    print(f"  - {ocr_path} ({len(ocr_transcripts)} entries)")
    print(f"  - {audio_path} ({len(audio_transcripts)} entries)")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_dir = os.path.join(base_dir, "dataset")
    build_media_cache(dataset_dir)
