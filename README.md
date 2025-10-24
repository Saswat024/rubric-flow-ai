# Rubric Flow AI

An intelligent evaluation platform for flowcharts, pseudocode, and algorithms using AI-powered assessment with advanced Control Flow Graph (CFG) analysis.

## Features

- **Flowchart Evaluation**: Upload flowchart images for comprehensive analysis
- **Pseudocode Assessment**: Submit code for detailed scoring and feedback
- **Document Processing**: Evaluate algorithms from PDF, DOCX, PPTX, and TXT files
- **Solution Comparison**: Compare two solutions using CFG analysis with visual representations
- **AI-Powered Scoring**: Uses Google Gemini AI for accurate evaluations
- **User Authentication**: Secure login and evaluation history tracking
- **Export Capabilities**: Generate PDF reports and CSV exports
- **Visual CFG Analysis**: Mermaid diagram generation for solution visualization
- **Detailed Feedback**: Structured rubric-based scoring with actionable insights

## Tech Stack

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui components
- React Router
- TanStack Query
- React Hook Form + Zod validation

### Backend
- FastAPI (Python)
- SQLite database
- Google Generative AI (Gemini)
- PIL for image processing
- Document parsing (PDF, DOCX, PPTX)
- Report generation (PDF, CSV)
- Control Flow Graph analysis
- bcrypt for password hashing

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
python start.py
```



## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Evaluation
- `POST /api/evaluate-flowchart` - Flowchart evaluation
- `POST /api/evaluate-pseudocode` - Pseudocode evaluation
- `POST /api/evaluate-document` - Document-based algorithm evaluation
- `GET /api/evaluations` - User evaluation history

### Comparison
- `POST /api/compare-solutions` - Compare two solutions using CFG analysis
- `GET /api/comparisons` - User comparison history

### Export
- `GET /api/export/pdf/{evaluation_id}` - Export single evaluation as PDF
- `GET /api/export/csv` - Export all evaluations as CSV
- `GET /api/export/comparison/{comparison_id}` - Export comparison as PDF

### Health
- `GET /health` - Health check endpoint

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

### Document-based Algorithms
- Algorithm Logic (40 pts)
- Implementation Quality (30 pts)
- Documentation (20 pts)
- Efficiency (10 pts)

### Solution Comparison
- Control Flow Graph analysis
- Structural similarity assessment
- Logic flow comparison
- Performance and efficiency evaluation
- Visual CFG representation with Mermaid diagrams

## Supported File Types

### Document Upload
- PDF (.pdf)
- Microsoft Word (.docx)
- PowerPoint (.pptx)
- Plain Text (.txt)

### Image Upload
- PNG, JPEG, JPG, GIF, BMP, WEBP formats for flowchart analysis
