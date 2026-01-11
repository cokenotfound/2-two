# 2^Two: Daily CSE Aptitude & Technical Quizzer

2^Two is a daily habit-building platform that provides 4 structured questions—2 Aptitude and 2 Core Technical—specifically curated for CSE interview preparation. The platform is designed around the philosophy of "Consistency over Accuracy," encouraging a 2-minute daily ritual to keep fundamental concepts fresh.

---

## Abstract
Preparing for technical interviews often suffers from "burst learning" followed by long periods of inactivity. 2^Two solves this by providing a deterministic daily challenge. By utilizing a date-based seed, the platform ensures every student globally solves the same set of hand-picked PYQs (Previous Year Questions) each day, fostering community discussion and long-term retention.

---

## Project Evolution

### 1st Iteration: Streamlit Prototype
The initial proof-of-concept was developed using the Streamlit framework for rapid prototyping.
* **Functionality**: Provided live question generation using LLMs.
* **Limitations**: High latency during generation and session state reset issues led to the decision to move toward a decoupled architecture.
* **Status**: Maintained as a legacy version for quick internal testing.

### 2nd Iteration: Full-Stack Architecture (Current)
To improve performance and data integrity, the project transitioned to a decoupled architecture. This version utilizes a high-performance backend and a lightweight, minimalist frontend.
* **Hybrid Strategy**: Questions are pulled from curated local banks while explanations are generated via real-time LLM inference.

---

## Key Features

* **Deterministic Daily Pool**: Uses a YYYYMMDD seed to select 4 specific questions from a bank of 500+, ensuring a shared global experience.
* **Asynchronous AI Logic**: While the questions are local for speed, the explanations are generated in real-time by the Deepseek-R1 LLM via OpenRouter.
* **Race-Condition Protection**: Implements AbortController in JavaScript to cancel pending API calls when navigating between questions, preventing logic leakage.
* **Dynamic Scoring Visuals**: Features a conditional UI that renders scores in red/green based on a 4/4 perfection threshold.
* **Philosophical Design**: Removes the "Restart" button to emphasize the importance of daily discipline over perfection.

---

## Technologies Used

### Frontend
* **HTML5 & CSS3**: Custom Stone Grey minimalist aesthetic with high-contrast serif typography.
* **Vanilla JavaScript**: Asynchronous Fetch API for backend communication, DOM manipulation, and AbortController for request management.

### Backend
* **FastAPI (Python)**: High-performance asynchronous framework for handling requests and LLM orchestration.
* **Pandas**: Used for deterministic sampling and data manipulation from local CSV files.
* **Uvicorn**: ASGI server implementation for production-grade hosting.

### Intelligence & Data
* **OpenRouter API**: Interface for Deepseek-R1 model to generate concise logical proofs.
* **CSV Repositories**: 500+ hand-picked Aptitude and Technical Previous Year Questions.

---

## Project Structure
```text
├── main.py                    # FastAPI server & route handlers
├── questions.py               # OpenRouter API integration logic
├── index.html                 # Frontend entry point (Logo links to intro)
├── requirements.txt           # Python dependencies (fastapi, pandas, etc.)
├── aptitudequestionbank.csv   # 250+ Curated Aptitude PYQs
└── technicalquestionbank.csv  # 250+ Curated Technical PYQs