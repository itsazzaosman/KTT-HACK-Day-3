import gradio as gr
import json
import random
import os
import whisper
import re
import numpy as np
import librosa
import numpy as np
import re


from adaptive import KnowledgeTracer
from database import init_db, log_attempt
import time

init_db()

kt = KnowledgeTracer()
current_skill_state = "counting"

# Load the curriculum
CURRICULUM_PATH = "data/T3.1_Math_Tutor/curriculum_full.json"
with open(CURRICULUM_PATH, "r", encoding="utf-8") as f:
    curriculum = json.load(f)



def load_random_item(language):
    """Adaptive item loader based on Bayesian Knowledge Tracing."""
    global current_skill_state
    
    lang_map = {"English": "en", "French": "fr", "Kinyarwanda": "kin"}
    lang_code = lang_map[language]
    
    # 1. Determine target difficulty based on student's past performance
    # We prioritize 'addition' for this demo, but you can track any skill
    target_difficulty = kt.get_next_difficulty("addition")
    
    # 2. Filter curriculum by target difficulty
    filtered_items = [i for i in curriculum if i['difficulty'] == target_difficulty]
    
    # Fallback if no items match that exact difficulty
    if not filtered_items:
        item = random.choice(curriculum)
    else:
        item = random.choice(filtered_items)
    
    current_skill_state = item.get('skill', 'counting')
    stem_text = item.get(f"stem_{lang_code}", "Text missing")
    audio_path = item.get(f"tts_{lang_code}", None)
    image_path = f"images/{item.get('visual', '')}.png"
    
    print(f"DEBUG: Adaptive Load | Skill: {current_skill_state} | Target Diff: {target_difficulty} | Item ID: {item['id']}")

    # Fallbacks for missing assets
    if not os.path.exists(image_path): image_path = None
    if not audio_path or not os.path.exists(audio_path): audio_path = None
        
    return stem_text, image_path, audio_path, item["answer_int"]

asr_model = whisper.load_model("tiny")



def process_audio(audio_filepath, correct_answer, language):
    """Transcribes, grades, and logs progress to SQLite."""
    if not audio_filepath:
        return "No audio detected. Please try again!"

    # Start timer to track Task 1 latency constraints
    start_time = time.time()

    try:
        # 1. ASR Pipeline (Load -> Transcribe)
        audio, sr = librosa.load(audio_filepath, sr=16000)
        lang_code = {"English": "en", "French": "fr", "Kinyarwanda": "rw"}.get(language, "en")
        
        result = asr_model.transcribe(audio, language=lang_code, fp16=False)
        transcription = result["text"].lower().strip()
        
        # 2. Answer Extraction
        numbers_found = re.findall(r'\d+', transcription)
        user_answer = int(numbers_found[0]) if numbers_found else None
        
        # 3. Logic & Scoring
        is_correct = (user_answer == int(correct_answer))
        
        # 4. Update Knowledge Tracer and SQLite Database
        end_time = time.time()
        latency = end_time - start_time
        
        log_attempt(current_skill_state, is_correct, latency)
        new_mastery = kt.update(current_skill_state, is_correct)
        
        # 5. Formulate Feedback
        if is_correct:
            feedback = f"✅ Correct! I heard '{transcription}'. Mastery: {new_mastery:.2f}"
        else:
            feedback = f"❌ I heard '{transcription}'. The answer was {correct_answer}."
            
        print(f"DEBUG: Feedback Sent | Latency: {latency:.2f}s | Correct: {is_correct}")
        return feedback

    except Exception as e:
        print(f"Error during ASR: {e}")
        return "⚠️ Error processing your voice. Please try speaking again."
    
    
    # --- Gradio User Interface ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧮 AI Math Tutor for Early Learners (P1-P3)")
    
    with gr.Row():
        lang_selector = gr.Radio(["English", "French", "Kinyarwanda"], value="Kinyarwanda", label="Tutor Language")
        next_btn = gr.Button("🎲 Load Next Question", variant="primary")
    
    with gr.Row():
        # Left Column: Tutor Output
        with gr.Column():
            gr.Markdown("### Tutor Presentation")
            question_text = gr.Textbox(label="Question Text", interactive=False)
            visual_display = gr.Image(label="Visual Grounding", type="filepath")
            tutor_audio = gr.Audio(label="Tutor Voice", interactive=False, autoplay=True)
            hidden_answer = gr.State() # Hidden state to store the correct answer
            
        # Right Column: Learner Input
        with gr.Column():
            gr.Markdown("### Learner Response")
            mic_input = gr.Audio(sources=["microphone"], type="filepath", label="Tap to Answer")
            feedback_text = gr.Textbox(label="Tutor Feedback")
            
    # Actions
# Actions
    next_btn.click(
        fn=load_random_item,
        inputs=[lang_selector],
        outputs=[question_text, visual_display, tutor_audio, hidden_answer]
    ).then(
        fn=lambda: (None, ""), # This clears the mic and the feedback text
        outputs=[mic_input, feedback_text]
    )
    
    mic_input.stop_recording(
        fn=process_audio,
        inputs=[mic_input, hidden_answer, lang_selector],
        outputs=[feedback_text]
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)