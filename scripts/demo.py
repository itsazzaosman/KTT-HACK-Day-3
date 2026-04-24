import gradio as gr
import json
import random
import os
import whisper
import re

# Load the curriculum
CURRICULUM_PATH = "data/T3.1_Math_Tutor/curriculum_full.json"
with open(CURRICULUM_PATH, "r", encoding="utf-8") as f:
    curriculum = json.load(f)



def load_random_item(language):
    item = random.choice(curriculum)
    lang_map = {"English": "en", "French": "fr", "Kinyarwanda": "kin"}
    lang_code = lang_map[language]
    
    stem_text = item.get(f"stem_{lang_code}", "Text missing")
    
    # Force lowercase for the filename to match how we saved them
    audio_path = item.get(f"tts_{lang_code}", None)
    image_path = f"images/{item.get('visual', '')}.png"
    
    # Debugging print - check your terminal to see if the path is correct!
    print(f"DEBUG: Loading Item {item['id']} | Audio Path: {audio_path}")

    if not audio_path or not os.path.exists(audio_path):
        print(f"⚠️ WARNING: Audio file not found at {audio_path}")
        audio_path = None
        
    return stem_text, image_path, audio_path, item["answer_int"]
        
    # We return: Stem Text, Image, Tutor Audio, and the hidden Answer (for grading later)
    return stem_text, image_path, audio_path, item["answer_int"]

asr_model = whisper.load_model("tiny")

def process_audio(audio_filepath, correct_answer, language):
    if not audio_filepath:
        return "No audio detected. Please try again!"

    # 1. Transcribe the audio
    # We specify the language to help the model be more accurate
    lang_code = {"English": "en", "French": "fr", "Kinyarwanda": "rw"}.get(language, "en")
    result = asr_model.transcribe(audio_filepath, language=lang_code)
    transcription = result["text"].lower().strip()
    
    # 2. Extract digits from the transcription
    # Kids might say "The answer is five" - we just want the "5"
    numbers_found = re.findall(r'\d+', transcription)
    
    # If the model transcribes words like "five", we need to handle that 
    # (In a full version, we'd use a word-to-number mapper)
    
    user_answer = None
    if numbers_found:
        user_answer = int(numbers_found[0])
    
    # 3. Grade the answer
    if user_answer == int(correct_answer):
        feedback = f"✅ Correct! You said '{transcription}'. Well done!"
    else:
        feedback = f"❌ Not quite. I heard '{transcription}'. The answer was {correct_answer}."
        
    return feedback

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
    next_btn.click(
        fn=load_random_item,
        inputs=[lang_selector],
        outputs=[question_text, visual_display, tutor_audio, hidden_answer]
    )
    
    mic_input.stop_recording(
        fn=process_audio,
        inputs=[mic_input, hidden_answer, lang_selector],
        outputs=[feedback_text]
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)