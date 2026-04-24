# Process Log: AIMS KTT Hackathon S2.T3.1 - AI Math Tutor

**Name:** Azza Osman

**Date:** 24/04/2026

---

## 1. Hour-by-Hour Timeline

*The 4-hour build process for the Offline AI Math Tutor (10:00 AM - 02:00 PM).*

* **Hour 1 (10:00 AM - 11:00 AM):**

  * [cite_start]Analyzed the **S2.T3.1 Candidate Brief** to align with the **< 75 MB footprint** and **fully offline** CPU constraints.
  * [cite_start]Developed `data_generator.py` to create a **75-item curriculum** (exceeding the required 60 items) covering Counting, Number Sense, Addition, Subtraction, and Word Problems.
  * [cite_start]Localized curriculum stems for Rwanda, ensuring correct interrogative phrasing in Kinyarwanda (e.g., using **"zingahe?"** for questions).
  * Implemented `os.makedirs` in the generator script to resolve `FileNotFoundError` and automate directory structures.
* **Hour 2 (11:00 AM - 12:00 PM):**

  * Implemented the **Offline Teacher TTS Pipeline**. [cite_start]Pivoted to a unified **Meta MMS (VITS)** approach for English, French, and Kinyarwanda to solve Python 3.12 compatibility issues with Coqui-TTS.
  * Developed a **Text Normalization** layer to convert digits into words (e.g., "20 + 10" to "Twenty plus ten"), resolving the issue where raw digits caused silent audio outputs.
  * [cite_start]Built `generate_visuals.py` using **Pillow** to procedurally generate 800x600 grid assets for counting tasks, meeting visual grounding requirements within a minimal disk footprint.
  * [cite_start]Created `make_synthetic_child.py` to generate the **synthetic numeracy dataset (1–55)**, applying **+6 semitone pitch-shifting** and **1.15x tempo perturbation** to mimic early learner voices.
* **Hour 3 (12:00 PM - 01:00 PM):**

  * [cite_start]Integrated the **Speech Recognition (ASR)** component using `openai/whisper-tiny` (39M parameters) to fit the strict on-device footprint.
  * [cite_start]Developed the `demo.py` logic to link the ASR transcription to the curriculum's `answer_int` for real-time scoring[cite: 33].
  * [cite_start]Implemented a basic **Knowledge Tracing** model (Bayesian Knowledge Tracing) to adapt question difficulty based on student performance.
* **Hour 4 (01:00 PM - 02:00 PM):**

  * [cite_start]Finalized the **Gradio UI** to include the microphone input loop and immediate feedback audio in the learner's dominant language.
  * [cite_start]Conducted a footprint audit using `du -sh` to verify the total app size remains **≤ 75 MB** excluding the TTS cache.
  * [cite_start]Drafted the **parent_report.py** to generate weekly visual progress summaries from the local SQLite store.
  * Signed the **Honor Code** in `SIGNED.md` and prepared the repository for the Live Defense.

---

## 2. LLM & Assistant Tool Usage

*Declaring tools used and the reasoning behind them.*

* **Tool 1: Gemini**
  * **Why I used it:** To rapidly generate localized math curriculum content in Kinyarwanda, to debug library compatibility issues between Coqui-TTS and Python 3.12, and to architect a procedural image generation system that satisfies visual grounding requirements without increasing the app's disk footprint[cite: 110, 111].

---

## 3. Sample Prompts

*Example of Prompts  taht  are actually used, and one discarded.*

### Used Prompts:

1. *"Write a Python script to generate a 75-item math curriculum JSON including 5 sub-skills with difficulty and age bands (5-9) localized for Rwanda."*
2. *"ERROR: No matching distribution found for TTS (Requires-Python >=3.9.0, <3.12). How can I run high-quality Kinyarwanda TTS offline on Python 3.12?"*
3. *"The MMS model is skipping numbers in '20 + 10'. Write a text normalizer to convert digits to words for EN, FR, and Kinyarwanda."*

### Discarded Prompt:

* *"Search for 1,000 images of goats and tomatoes on Google and write a script to download them."*
  * **Why I discarded it:** Downloading 1,000 high-resolution images would have instantly violated the **75 MB hard footprint limit**[cite: 83]. I decided instead to procedurally generate lightweight geometric grids using Pillow, which keeps the total visual asset size under 2 MB.

---

## 4. The Single Hardest Decision

The single hardest technical decision was abandoning the suggested **Coqui-TTS/Piper** workflow in favor of a unified **Meta MMS** pipeline. While the brief suggested Piper, the dependency conflicts with modern Python environments (3.12) posed a significant risk to the **Live Defense** stability[cite: 115]. By switching to Meta MMS for all three languages, I was able to implement a **Text Normalization** layer that ensures the tutor correctly pronounces equations a feature the standard models lacked. This decision required more manual coding for text-to-word mapping, but it guaranteed a high-fidelity, fully offline experience that remains well under the 75 MB limit while providing superior phonetic accuracy for the target demographic[cite: 82, 83].
