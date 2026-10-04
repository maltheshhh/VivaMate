# VivaMate

> **Your AI-powered companion for viva, interview, and placement preparation.**

VivaMate is a local-first AI interview preparation assistant designed to help students practice technical interviews, HR rounds, DSA questions, project discussions, and resume-based interviews.

It combines conversational AI, voice input, personalized candidate context, performance scoring, readiness tracking, weak-topic detection, and downloadable reports into a single lightweight web application.

The application can run **entirely locally** using [Ollama](https://ollama.com/), making it possible to practice without sending your conversations to a cloud AI provider.

---

## Features

### AI Interview Modes

VivaMate provides multiple focused preparation modes:

- **Mock Interview** — Practice realistic interview questions one at a time.
- **Explain Mode** — Learn concepts you struggled with through simple explanations and examples.
- **HR Round** — Practice behavioral and situational questions using STAR-style feedback.
- **DSA Round** — Practice data structures and algorithms questions, including approach and complexity.
- **Project Deep-Dive** — Discuss your GitHub projects, design decisions, trade-offs, bugs, and testing.
- **Resume Roast** — Receive direct feedback and line-level improvement suggestions for your resume.
- **Session Report** — Generate a summary of strengths, weaknesses, and revision topics.

### Personalized Preparation

VivaMate allows you to provide:

- Name
- Target role
- GitHub username
- Resume PDF

The application extracts resume content and retrieves public GitHub repositories so the AI can use your background while conducting interviews.

### Performance Tracking

VivaMate evaluates answers during graded interview modes and tracks:

- Answer score
- Clarity score
- Topic performance
- Weak areas
- Practice streak
- Overall readiness

### Readiness Score

The application generates a readiness score based on your:

- Average answer performance
- Answer clarity
- Number of topics practiced

This gives you a simple way to track your interview preparation progress.

### Voice Interaction

VivaMate supports microphone-based answers using:

- Browser audio capture
- `faster-whisper`
- Local speech-to-text processing

You can also enable **Read Replies Aloud** using the browser's speech synthesis API.

### Pressure Mode

Enable **Pressure Mode** to simulate a time-constrained interview.

Each question receives a 60-second response timer, helping you practice answering under realistic interview pressure.

### Quick Commands

VivaMate includes shortcuts for common preparation workflows:

```text
/quiz
/weak
/resume-tips
/hr
/report
```

For example:

```text
/quiz
```

starts a rapid-fire DSA quiz.

```text
/weak
```

asks VivaMate to focus on your weakest topic.

### Reports and Sharing

Generate a PDF session report containing:

- Readiness score
- Practice streak
- Number of answers
- Strengths
- Weaknesses
- Recommended revision topics

You can also generate a shareable result card containing your readiness score.

### Local-First Architecture

The default configuration uses:

```text
Browser
   │
   ▼
FastAPI Backend
   │
   ├── SQLite
   │
   ├── Ollama
   │     └── Local LLM
   │
   └── faster-whisper
         └── Local Speech-to-Text
```

Your interview conversations can therefore remain on your machine when using local mode.

---

## Tech Stack

### Backend

- **Python**
- **FastAPI**
- **SQLite**
- **HTTPX**
- **Uvicorn**

### AI

- **Ollama**
- Default model: `qwen2.5:7b`
- Optional OpenAI-compatible cloud API
- **faster-whisper** for speech-to-text

### Frontend

- HTML
- CSS
- Vanilla JavaScript
- Browser Speech Synthesis API
- MediaRecorder API

### Document Processing

- **pypdf** — Resume PDF text extraction
- **ReportLab** — PDF report generation

### External Integration

- GitHub public API for repository information

---

## Architecture

```text
                         ┌─────────────────────┐
                         │      Browser        │
                         │                     │
                         │ HTML / CSS / JS     │
                         │ Chat UI             │
                         │ Voice Input         │
                         │ Readiness Dashboard │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      Backend        │
                         ├─────────────────────┤
                         │ Chat                │
                         │ Evaluation          │
                         │ Profile             │
                         │ Transcription       │
                         │ Reports             │
                         │ Settings            │
                         └──────┬───────┬──────┘
                                │       │
                   ┌────────────┘       └─────────────┐
                   ▼                                  ▼
          ┌────────────────┐                 ┌─────────────────┐
          │    SQLite      │                 │   AI Provider   │
          │                │                 │                 │
          │ Profile        │                 │ Ollama          │
          │ Messages       │                 │ or Cloud API    │
          │ Scores         │                 └─────────────────┘
          │ Settings       │
          └────────────────┘

                         ┌─────────────────────┐
                         │ faster-whisper      │
                         │                     │
                         │ Voice → Text        │
                         └─────────────────────┘
```

---

## Project Structure

```text
VivaMate/
└── vivamate/
    ├── main.py
    ├── index.html
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── vivamate.db
```

### Important Files

| File | Description |
|---|---|
| `main.py` | FastAPI backend, AI integration, database logic, evaluation, reports and API endpoints |
| `index.html` | Complete frontend UI and client-side application logic |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variable template |
| `vivamate.db` | SQLite database created by the application at runtime |

---

## Getting Started

### Prerequisites

Make sure you have:

- Python 3.9+
- pip
- Ollama
- A local Ollama-compatible model

Install Ollama from:

https://ollama.com/

---

## Installation

Clone the repository:

```bash
git clone https://github.com/maltheshhh/VivaMate.git
cd VivaMate/vivamate
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Configure Ollama

Start Ollama and download the default model:

```bash
ollama pull qwen2.5:7b
```

The application uses:

```text
qwen2.5:7b
```

by default.

Ollama normally runs at:

```text
http://localhost:11434
```

---

## Environment Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

The default configuration is:

```env
VIVAMATE_API_KEY=
VIVAMATE_API_BASE=
VIVAMATE_MODEL=
```

For local usage, these values can remain empty.

VivaMate automatically falls back to:

```text
qwen2.5:7b
```

when `VIVAMATE_MODEL` is not specified.

---

## Run VivaMate

Start the FastAPI server:

```bash
uvicorn main:app --port 8000
```

Then open:

```text
http://localhost:8000
```

You should see the VivaMate interface.

---

## First-Time Setup

After launching VivaMate:

1. Click **Setup**.
2. Enter your name.
3. Enter your target role.
4. Enter your GitHub username.
5. Upload your resume as a PDF.
6. Save your profile.
7. Select an interview mode.
8. Start practicing.

VivaMate will use your resume and GitHub information to personalize the interview experience.

---

## Cloud AI Mode

VivaMate also supports an optional OpenAI-compatible cloud API.

Add the following to `.env`:

```env
VIVAMATE_API_KEY=your_api_key
VIVAMATE_API_BASE=https://api.openai.com/v1
VIVAMATE_MODEL=your_model
```

Restart the application:

```bash
uvicorn main:app --port 8000
```

Then open:

**Settings → Cloud**

The API key is used by the backend and is not sent to the browser.

> For privacy-sensitive preparation, local Ollama mode is recommended.

---

## Offline Mode

VivaMate is designed to continue working locally after the required models have been downloaded.

For speech recognition, the first microphone use downloads the `faster-whisper` `base` model.

After the model is available locally, you can test the application without an internet connection.

### Offline workflow

```text
Internet
   │
   ├── Download Ollama model
   └── Download Whisper model
             │
             ▼
       Local machine
             │
             ▼
       VivaMate
```

GitHub repository ingestion requires internet access during profile setup because VivaMate retrieves repository information from GitHub's public API.

---

## API Endpoints

VivaMate exposes a lightweight FastAPI backend.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Serve the VivaMate web application |
| `POST` | `/api/chat` | Send messages and receive streamed AI responses |
| `GET` | `/api/report` | Retrieve preparation report |
| `GET` | `/api/readiness` | Retrieve readiness score and streak |
| `GET` | `/api/export` | Export preparation report as PDF |
| `GET` | `/api/profile` | Retrieve candidate profile |
| `POST` | `/api/profile` | Save profile and process resume/GitHub information |
| `POST` | `/api/transcribe` | Convert recorded audio into text |
| `GET` | `/api/settings` | Retrieve AI mode settings |
| `POST` | `/api/settings` | Change local/cloud AI mode |

---

## Database

VivaMate uses SQLite and automatically creates the database tables required by the application.

The main tables are:

### `profile`

Stores candidate information:

```text
name
role
github
resume
repos
```

### `msgs`

Stores conversation history:

```text
session
role
content
```

### `scores`

Stores interview evaluation data:

```text
session
topic
score
clarity
day
```

### `kv`

Stores application settings such as the selected AI mode.

---

## How Answer Evaluation Works

During graded modes, VivaMate evaluates the candidate's previous question and current answer.

The AI evaluator returns structured information containing:

```json
{
  "score": 0,
  "clarity": 0,
  "topic": "topic"
}
```

The score and topic are then stored in SQLite and used to calculate:

- Weak topics
- Strengths
- Readiness
- Practice streak
- Revision recommendations
- Badges

---

## Readiness Calculation

The readiness score combines:

- Average answer score
- Number of distinct topics practiced
- Average clarity

The score is presented as a value out of 100.

This is intended as a **practice metric**, not a prediction of actual interview performance.

---

## Privacy

VivaMate is designed with a local-first approach.

When using local mode:

```text
Your Browser
     ↓
Your FastAPI Server
     ↓
Your SQLite Database
     ↓
Your Local Ollama Model
```

Interview conversations can remain entirely on your local machine.

Cloud mode is optional and requires explicitly configuring a compatible API provider.

---

## Security Notes

For local development:

- Keep `.env` out of version control.
- Never commit API keys.
- Run the application behind appropriate authentication before exposing it publicly.
- Review the privacy implications before using cloud AI providers with personal resumes or interview data.

---

## Future Improvements

Potential future enhancements include:

- Authentication and multi-user support
- More interview-specific AI evaluation
- Advanced resume parsing
- Better GitHub project analysis
- Interview history dashboard
- Topic-wise progress charts
- Custom interview question sets
- Company-specific interview preparation
- Kannada and multilingual interview support
- More advanced voice interaction
- Persistent interview sessions
- Improved report generation
- Docker deployment
- Production-grade database support
- Automated interview difficulty adjustment

---

## Contributing

Contributions are welcome.

### 1. Fork the repository

```bash
git fork https://github.com/maltheshhh/VivaMate.git
```

Or fork it directly from GitHub.

### 2. Clone your fork

```bash
git clone https://github.com/<your-username>/VivaMate.git
cd VivaMate/vivamate
```

### 3. Create a branch

```bash
git checkout -b feature/your-feature
```

### 4. Make your changes

Test the application locally:

```bash
uvicorn main:app --port 8000
```

### 5. Commit your changes

```bash
git add .
git commit -m "feat: add your feature"
```

### 6. Push your branch

```bash
git push origin feature/your-feature
```

### 7. Open a Pull Request

Describe:

- What you changed
- Why the change was needed
- How you tested it

---

## Development

A simple development workflow is:

```bash
python -m venv .venv
```

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
ollama pull qwen2.5:7b
```

```bash
uvicorn main:app --reload --port 8000
```

The `--reload` option automatically restarts the server when Python source files change.

---

## Use Cases

VivaMate can be useful for:

- College viva preparation
- Technical interview preparation
- Campus placement preparation
- DSA practice
- HR interview preparation
- Project explanation practice
- Resume improvement
- Interview communication practice
- Last-minute interview revision
- Continuous interview preparation

---

## Why VivaMate?

Traditional interview preparation often involves switching between multiple platforms:

```text
Resume → YouTube → DSA Platform → Mock Interview → Notes → Progress Tracking
```

VivaMate aims to bring these workflows together:

```text
                 ┌────────────────────┐
                 │      VivaMate      │
                 ├────────────────────┤
                 │ Mock Interviews    │
                 │ DSA Practice       │
                 │ HR Practice        │
                 │ Project Questions  │
                 │ Resume Feedback    │
                 │ Voice Practice     │
                 │ Performance Score  │
                 │ Progress Tracking  │
                 │ Reports            │
                 └────────────────────┘
```

The goal is simple:

> **Practice. Get evaluated. Identify weaknesses. Improve. Repeat.**

---

## License

Add your preferred open-source license to the repository before publishing this project for public reuse.

For example:

```text
MIT License
```

If using the MIT License, add a `LICENSE` file containing the official MIT License text.

---

## Author

**Malthesh**

GitHub:

https://github.com/maltheshhh

Project:

https://github.com/maltheshhh/VivaMate

---

## VivaMate

**Practice smarter. Prepare better. Face your interview with confidence.**
