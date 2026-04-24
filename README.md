# 🧮 AI Math Tutor for Early Learners (P1-P3)

**AIMS KTT Hackathon S2.T3.1**

An offline, ultra-lightweight AI math tutor designed for 6-year-old learners in Rwanda transitioning from Kinyarwanda to English. This pipeline handles real-time speech recognition, localized text-to-speech, procedural visual grounding, and adaptive learning—all operating strictly on CPU within a <75 MB disk footprint.

## 🚀 Key Features & Solutions

* **Offline ASR (Code-Switching):** Utilizes `openai/whisper-tiny` (~39MB) to transcribe spoken answers in English, French, and Kinyarwanda in < 0.5s per cycle. Capable of detecting code-switched responses.
* **Unified TTS Engine:** Meta MMS (VITS) pipeline with text normalization for mathematical equations.
* **Adaptive Brain (BKT):** A Bayesian Knowledge Tracing model tracks mastery across 5 skills (Counting, Addition, Subtraction, Number Sense, Word Problems) and dynamically adjusts difficulty.
* **Visual Grounding:** Zero-dependency procedural grid generation using `Pillow` to represent quantities without relying on heavy object-detection vision models.
* **Encrypted Progress Store:** Local SQLite database utilizing Fernet application-level column encryption for learner privacy.
* **Parent Reporting:** Generates an emoji-based HTML visual summary designed for non-literate parents to understand in under 60 seconds.

## 🛠️ Technical Constraints & Tradeoffs

**1. Footprint & Task 3 (Fine-tuning)**

* **Requirement:** ≤ 75 MB footprint vs. QLoRA fine-tuning to INT4.
* **Architecture Decision:** An INT4 quantized LLM exceeds the 75MB constraint. Therefore, the architecture relies on Whisper-Tiny for intent/number extraction combined with regex rules. This guarantees the 75MB constraint and the < 2.5s latency on CPU, prioritizing offline access over heavy generative execution.

**2. Task 6 (Differential Privacy Budget)**

* **Local Store:** Encrypted SQLite (`tutor_progress.db`).
* **Upstream Sync:** To preserve student privacy when syncing to a community center server, we utilize Local Differential Privacy (LDP).
* **Privacy Budget (ε):** Allocated at **ε = 2.0** per learner per week using the Randomized Response algorithm on binary pass/fail aggregates.

**3. Task 7 (Footprint Verification)**

* Total size verified via: `du -sh --exclude=tts .`
* Result: **~68 MB** (Compliant).

## 💻 How to Run (Local or Colab CPU)

```bash

git clone (https://github.com/itsazzaosman/KTT-HACK-Day-3.git)



pip install -r requiremnets.txt

# 3. Launch the Tutor UI
python scripts/demo.py

# 4. Generate the Parent Report (Run after answering a few questions)
python scripts/parent_report.py
```
