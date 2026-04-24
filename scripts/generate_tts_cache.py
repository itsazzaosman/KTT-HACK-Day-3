import os
import json
import time
from gtts import gTTS

# =====================================================================
# from TTS.api import TTS
# tts_model_en = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
# tts_model_fr = TTS(model_name="tts_models/fr/css10/vits", progress_bar=False, gpu=False)
# =====================================================================

def ensure_directories():
    """Create the TTS cache directories if they don't exist."""
    dirs = ['tts/en', 'tts/fr', 'tts/kin']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Verified directory: {d}")

def generate_audio(text, lang, filepath):
    """
    Generates audio using gTTS. 
    (Swap this logic with Coqui/Piper for the final offline submission)
    """
    # Kinyarwanda ('rw') isn't officially supported by standard gTTS, 
    # so we fallback to French pronunciation rules for Kinyarwanda text as a hackathon workaround.
    tts_lang = 'fr' if lang == 'kin' else lang 
    
    try:
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        tts.save(filepath)
        
        # OFFLINE COQUI-TTS EQUIVALENT:
        # if lang == 'en':
        #     tts_model_en.tts_to_file(text=text, file_path=filepath)
        # elif lang == 'fr' or lang == 'kin':
        #     tts_model_fr.tts_to_file(text=text, file_path=filepath)
            
    except Exception as e:
        print(f"Error generating audio for '{text}': {e}")

def process_curriculum():
    json_path = "data/T3.1_Math_Tutor/curriculum_full.json"
    
    if not os.path.exists(json_path):
        print(f"Error: Could not find {json_path}. Run the data generator first.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        curriculum = json.load(f)

    print(f"Loaded {len(curriculum)} items. Starting TTS generation...")
    
    for item in curriculum:
        item_id = item['id'].lower()
        
        # Define paths based on the JSON structure
        path_en = f"tts/en/{item_id}.wav"
        path_fr = f"tts/fr/{item_id}.wav"
        path_kin = f"tts/kin/{item_id}.wav"

        # Generate English
        if 'stem_en' in item and not os.path.exists(path_en):
            print(f"Generating EN: {item['stem_en']}")
            generate_audio(item['stem_en'], 'en', path_en)
            
        # Generate French
        if 'stem_fr' in item and not os.path.exists(path_fr):
            print(f"Generating FR: {item['stem_fr']}")
            generate_audio(item['stem_fr'], 'fr', path_fr)
            
        # Generate Kinyarwanda
        if 'stem_kin' in item and not os.path.exists(path_kin):
            print(f"Generating KIN: {item['stem_kin']}")
            generate_audio(item['stem_kin'], 'kin', path_kin)
            
        # Small sleep to prevent API blocking if using gTTS online
        time.sleep(0.5) 

    print("\n✅ TTS Generation Complete! Audio files cached in the /tts folder.")

if __name__ == "__main__":
    ensure_directories()
    process_curriculum()