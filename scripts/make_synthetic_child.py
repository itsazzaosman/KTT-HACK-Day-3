import os
import time
import torch
import scipy.io.wavfile
import librosa
import soundfile as sf
import numpy as np
from gtts import gTTS
from transformers import VitsModel, AutoTokenizer

# Paths
AUDIO_OUT_DIR = 'data/child_utterances/synthetic'
os.makedirs(AUDIO_OUT_DIR, exist_ok=True)

#OAD THE MMS MODEL FOR KINYARWANDA
print("Loading Meta MMS Kinyarwanda TTS Model...")
mms_model_id = "facebook/mms-tts-kin"
kin_tokenizer = AutoTokenizer.from_pretrained(mms_model_id)
kin_model = VitsModel.from_pretrained(mms_model_id)
print("Model loaded successfully!")

# Vocab for numbers 1-10 (Expandable to 20) to test the ASR
numbers_vocab = {
    "en": [
        "one", "two", "three", "four", "five", "six", "seven", "eight", "ten",
        "eleven", "twelve", "thirteen", "fourteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
        "twenty-one", "twenty-two", "twenty-three", "twenty-six", "twenty-seven", "twenty-eight", "twenty-nine", "thirty",
        "thirty-one", "thirty-two", "thirty-three", "thirty-seven", "forty", "forty-one", "forty-three", "forty-six", "fifty-four", "fifty-five"
    ],
    "fr": [
        "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "dix",
        "onze", "douze", "treize", "quatorze", "seize", "dix-sept", "dix-huit", "dix-neuf", "vingt",
        "vingt et un", "vingt-deux", "vingt-trois", "vingt-six", "vingt-sept", "vingt-huit", "vingt-neuf", "trente",
        "trente et un", "trente-deux", "trente-trois", "trente-sept", "quarante", "quarante et un", "quarante-trois", "quarante-six", "cinquante-quatre", "cinquante-cinq"
    ],
    "kin": [
        "rimwe", "kabiri", "gatatu", "kane", "gatanu", "gatandatu", "karindwi", "umunani", "icumi",
        "cumi na rimwe", "cumi na kabiri", "cumi na gatatu", "cumi na kane", "cumi na gatandatu", "cumi na karindwi", "cumi n'umunani", "cumi n'icyenda", "makumyabiri",
        "makumyabiri na rimwe", "makumyabiri na kabiri", "makumyabiri na gatatu", "makumyabiri na gatandatu", "makumyabiri na karindwi", "makumyabiri n'umunani", "makumyabiri n'icyenda", "mirongo itatu",
        "mirongo itatu na rimwe", "mirongo itatu na kabiri", "mirongo itatu na gatatu", "mirongo itatu na karindwi", "mirongo ine", "mirongo ine na rimwe", "mirongo ine na gatatu", "mirongo ine na gatandatu", "mirongo itanu na kane", "mirongo itanu na gatanu"
    ]
}

def generate_mms_audio(text, output_path):
    """Generates Kinyarwanda audio using Meta's local MMS model."""
    inputs = kin_tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = kin_model(**inputs).waveform
    audio_data = output[0].numpy()
    scipy.io.wavfile.write(output_path, rate=kin_model.config.sampling_rate, data=audio_data)

def augment_to_child(input_path, output_path, pitch_steps=6.0, tempo_rate=1.15):
    """Applies pitch shift, tempo stretch, and synthetic noise to mimic a child in a classroom."""
    try:
        y, sr = librosa.load(input_path, sr=16000)
        
        # Pitch Shifting (+6 semitones)
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_steps)
        
        # Tempo Perturbation (+15% speed)
        y_child = librosa.effects.time_stretch(y_shifted, rate=tempo_rate)
        
        # Synthetic white noise (since we don't have MUSAN downloaded yet)
        synthetic_noise = np.random.normal(0, 0.005, len(y_child))
        y_final = y_child + synthetic_noise

        sf.write(output_path, y_final, sr)
    except Exception as e:
        print(f"Error augmenting {input_path}: {e}")

def main():
    print(f"Starting synthetic child utterance generation...")
    
    for lang, words in numbers_vocab.items():
        for i, word in enumerate(words):
            number_val = i + 1
            base_filename = f"base_{lang}_{number_val}.wav"
            final_filename = f"child_{lang}_{number_val}.wav"
            
            base_path = os.path.join(AUDIO_OUT_DIR, base_filename)
            final_path = os.path.join(AUDIO_OUT_DIR, final_filename)
            
            # 1. Generate base adult audio
            if lang == "kin":
                generate_mms_audio(word, base_path)
            else:
                tts = gTTS(text=word, lang=lang)
                tts.save(base_path)
            
            # Augment to sound like a child
            augment_to_child(base_path, final_path)
            
            #Clean up the base adult file
            if os.path.exists(base_path):
                os.remove(base_path)
                
            print(f"Generated synthetic child audio for: '{word}' ({lang})")
            time.sleep(0.5)

    print(f"\n✅ All child utterances generated in {AUDIO_OUT_DIR}")

if __name__ == "__main__":
    main()