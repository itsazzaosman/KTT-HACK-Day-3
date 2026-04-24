import os
import json
import torch
import scipy.io.wavfile
import re
from transformers import VitsModel, AutoTokenizer
from num2words import num2words

# --- CONFIGURATION ---
CURRICULUM_PATH = "data/T3.1_Math_Tutor/curriculum_full.json"
OUTPUT_DIRS = ['tts/en', 'tts/fr', 'tts/kin']

def ensure_directories():
    """Create the TTS cache directories if they don't exist."""
    for d in OUTPUT_DIRS:
        os.makedirs(d, exist_ok=True)

def normalize_text(text, lang):
    """
    Converts digits and symbols into spoken words so MMS can pronounce them.
    Example: '20 + 10' -> 'twenty plus ten'
    """
    # Find all numbers in the string
    numbers = re.findall(r'\d+', text)
    for num in numbers:
        if lang == 'en':
            word = num2words(int(num), lang='en')
        elif lang == 'fr':
            word = num2words(int(num), lang='fr')
        elif lang == 'kin':
            # Kinyarwanda number mapping for foundational math
            kin_map = {
                "1": "rimwe", "2": "kabiri", "3": "gatatu", "4": "kane", "5": "gatanu",
                "6": "gatandatu", "7": "karindwi", "8": "umunani", "9": "icyenda", "10": "icumi",
                "12": "cumi na kabiri", "14": "cumi na kane", "15": "cumi na gatanu",
                "17": "cumi na karindwi", "18": "cumi n'umunani", "20": "makumyabiri", 
                "30": "mirongo itatu", "40": "mirongo ine", "50": "mirongo itanu"
            }
            word = kin_map.get(num, num) 
        
        text = text.replace(num, word, 1)
    
    # Handle mathematical symbols for the TTS engine
    if lang == 'en':
        text = text.replace("+", " plus ").replace("-", " minus ").replace("=", " equals ")
    elif lang == 'fr':
        text = text.replace("+", " plus ").replace("-", " moins ").replace("=", " égale ")
    elif lang == 'kin':
        text = text.replace("+", " n' ").replace("-", " uvanyemo ").replace("=", " ni ")

    return text

def setup_offline_models():
    """Loads Meta MMS models. Requires ~150MB of RAM per model."""
    print("Loading Offline Models (This takes a moment on first run)...")
    models = {}
    
    lang_ids = {
        'en': "facebook/mms-tts-eng",
        'fr': "facebook/mms-tts-fra",
        'kin': "facebook/mms-tts-kin"
    }

    for lang, model_id in lang_ids.items():
        print(f" -> Loading {lang} Model...")
        models[lang] = {
            'tokenizer': AutoTokenizer.from_pretrained(model_id),
            'model': VitsModel.from_pretrained(model_id)
        }
    return models

def generate_audio(text, filepath, lang, models):
    """Normalizes text and generates audio file."""
    clean_text = normalize_text(text, lang)
    tokenizer = models[lang]['tokenizer']
    model = models[lang]['model']

    inputs = tokenizer(clean_text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    
    audio_data = output.squeeze().cpu().numpy()
    scipy.io.wavfile.write(filepath, rate=model.config.sampling_rate, data=audio_data)

def main():
    ensure_directories()
    
    if not os.path.exists(CURRICULUM_PATH):
        print(f"Error: {CURRICULUM_PATH} not found.")
        return

    with open(CURRICULUM_PATH, 'r', encoding='utf-8') as f:
        curriculum = json.load(f)

    models = setup_offline_models()
    print(f"\nProcessing {len(curriculum)} items...")

    for item in curriculum:
        item_id = item['id'].lower()
        
        # Define paths
        tasks = [
            ('en', f"tts/en/{item_id}.wav", 'stem_en'),
            ('fr', f"tts/fr/{item_id}.wav", 'stem_fr'),
            ('kin', f"tts/kin/{item_id}.wav", 'stem_kin')
        ]

        for lang_code, path, json_key in tasks:
            if json_key in item:
                # Force regeneration if the file is very small (indicates a failed silent generation)
                should_generate = not os.path.exists(path) or os.path.getsize(path) < 1000
                
                if should_generate:
                    print(f"Generating [{lang_code}] for {item_id}: {item[json_key]}")
                    generate_audio(item[json_key], path, lang_code, models)

    print("\n✅ All Tutor audio files are now clear and normalized.")

if __name__ == "__main__":
    main()