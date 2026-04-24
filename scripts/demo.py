import gradio as gr
import json
import random
import os

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

def process_audio(audio_filepath, correct_answer):
    """
    This is where the ASR model will go. 
    For now, it's a dummy function that just acknowledges the recording.
    """
    if not audio_filepath:
        return "No audio detected."
    
    # TODO: Pass 'audio_filepath' to Whisper/MMS to get the transcript
    # TODO: Compare transcript to 'correct_answer'
    
    return f"Audio received! (Next step: Transcribe and check if they said {correct_answer})"

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
        inputs=[mic_input, hidden_answer],
        outputs=[feedback_text]
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)