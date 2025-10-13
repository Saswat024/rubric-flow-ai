# Rubric Flow AI

An intelligent evaluation platform for flowcharts and pseudocode using AI-powered assessment.

## Features

- **Flowchart Evaluation**: Upload flowchart images for comprehensive analysis
- **Pseudocode Assessment**: Submit code for detailed scoring and feedback
- **AI-Powered Scoring**: Uses Google Gemini AI for accurate evaluations
- **User Authentication**: Secure login and evaluation history tracking
- **Detailed Feedback**: Structured rubric-based scoring with actionable insights

## Tech Stack

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui components

### Backend
- FastAPI (Python)
- SQLite database
- Google Generative AI (Gemini)
- PIL for image processing

## Setup

### Prerequisites
- Node.js & npm
- Python 3.8+
- Google AI API key

### Frontend Setup
```bash
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create .env file with:
# GOOGLE_API_KEY=your_api_key_here

python start.py
```

## API Endpoints

- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/evaluate-flowchart` - Flowchart evaluation
- `POST /api/evaluate-pseudocode` - Pseudocode evaluation
- `GET /api/evaluations` - User evaluation history

## Evaluation Criteria

### Flowcharts
- Start/End Presence (10 pts)
- Decision Nodes (30 pts)
- Completeness (30 pts)
- Flow Direction (20 pts)
- Label Clarity (10 pts)

### Pseudocode
- Correctness (50 pts)
- Edge Case Handling (20 pts)
- Clarity (15 pts)
- Complexity (15 pts)
