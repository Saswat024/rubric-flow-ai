from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import base64
from evaluators.flowchart import evaluate_flowchart
from evaluators.pseudocode import evaluate_pseudocode
from evaluators.algorithm import evaluate_algorithm
from parsers.document_parser import parse_document
from export.report_generator import generate_pdf_report, generate_csv_report
from database import (
    create_user, verify_user, create_session, verify_session, 
    delete_session, get_user_email, save_evaluation, get_user_evaluations
)

app = FastAPI()

# Enable CORS for local React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:8080", 
        "http://localhost:3000",
        "https://*.railway.app",
        "https://*.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PseudocodeRequest(BaseModel):
    code: str

class FlowchartRequest(BaseModel):
    image: str  # base64 encoded image

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class DocumentRequest(BaseModel):
    file: str  # base64 encoded file
    file_type: str  # .pdf, .docx, .pptx, .txt

# Dependency to get current user from token
async def get_current_user(authorization: Optional[str] = Header(None)) -> int:
    print(f"Authorization header: {authorization}")
    
    if not authorization:
        print("No authorization header provided")
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        print(f"Invalid authorization format: {authorization}")
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    print(f"Extracted token: {token[:10]}...")
    
    user_id = verify_session(token)
    print(f"User ID from token: {user_id}")
    
    if not user_id:
        print("Token verification failed")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id

@app.post("/api/auth/signup")
async def signup(request: SignupRequest):
    success, message = create_user(request.email, request.password)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    user_id = verify_user(request.email, request.password)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session(user_id)
    email = get_user_email(user_id)
    
    return {"token": token, "email": email}

@app.post("/api/auth/logout")
async def logout(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    success = delete_session(token)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to logout")
    
    return {"message": "Logged out successfully"}

@app.get("/api/auth/me")
async def get_me(user_id: int = Depends(get_current_user)):
    email = get_user_email(user_id)
    return {"email": email, "user_id": user_id}

@app.post("/api/evaluate-flowchart")
async def api_evaluate_flowchart(request: FlowchartRequest, user_id: int = Depends(get_current_user)):
    print("\n=== FLOWCHART REQUEST RECEIVED ===")
    try:
        print(f"User ID: {user_id}")
        print("Starting flowchart evaluation...")
        result = await evaluate_flowchart(request.image)
        print("Evaluation successful!")
        # Save evaluation to database
        save_evaluation(user_id, 'flowchart', 'image_data', result)
        return result
    except Exception as e:
        print(f"\n!!! ERROR in flowchart evaluation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate-pseudocode")
async def api_evaluate_pseudocode(request: PseudocodeRequest, user_id: int = Depends(get_current_user)):
    print("\n=== PSEUDOCODE REQUEST RECEIVED ===")
    try:
        print(f"User ID: {user_id}")
        print("Starting pseudocode evaluation...")
        result = await evaluate_pseudocode(request.code)
        print("Evaluation successful!")
        # Save evaluation to database
        save_evaluation(user_id, 'pseudocode', request.code[:500], result)
        return result
    except Exception as e:
        print(f"\n!!! ERROR in pseudocode evaluation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate-document")
async def api_evaluate_document(request: DocumentRequest, user_id: int = Depends(get_current_user)):
    """Evaluate algorithm/pseudocode from uploaded documents (.pdf, .docx, .pptx, .txt)"""
    print("\n=== DOCUMENT EVALUATION REQUEST RECEIVED ===")
    try:
        print(f"User ID: {user_id}")
        print(f"File type: {request.file_type}")
        
        # Parse document to extract text
        parsed_result = await parse_document(request.file, request.file_type)
        
        if not parsed_result['success']:
            raise HTTPException(status_code=400, detail=parsed_result.get('error', 'Failed to parse document'))
        
        extracted_text = parsed_result['text']
        print(f"Extracted text length: {len(extracted_text)} characters")
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text content found in document")
        
        # Evaluate the extracted algorithm/pseudocode
        print("Starting algorithm evaluation...")
        result = await evaluate_algorithm(extracted_text, eval_type="document")
        print("Evaluation successful!")
        
        # Save evaluation to database
        save_evaluation(user_id, 'document', extracted_text[:500], result)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n!!! ERROR in document evaluation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluations")
async def api_get_evaluations(user_id: int = Depends(get_current_user)):
    """Get user's evaluation history"""
    try:
        evaluations = get_user_evaluations(user_id)
        return evaluations
    except Exception as e:
        print(f"Error fetching evaluations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/pdf/{evaluation_id}")
async def api_export_pdf(evaluation_id: int, user_id: int = Depends(get_current_user)):
    """Export a single evaluation as PDF report"""
    try:
        # Get the specific evaluation
        evaluations = get_user_evaluations(user_id, limit=1000)
        evaluation = next((e for e in evaluations if e['id'] == evaluation_id), None)
        
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        user_email = get_user_email(user_id)
        
        # Generate PDF
        pdf_bytes = generate_pdf_report(evaluation['result'], user_email)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=evaluation_{evaluation_id}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/csv")
async def api_export_csv(user_id: int = Depends(get_current_user)):
    """Export all evaluations as CSV"""
    try:
        evaluations = get_user_evaluations(user_id, limit=1000)
        
        # Prepare data for CSV
        csv_data = []
        for eval_item in evaluations:
            csv_data.append({
                'created_at': eval_item['created_at'],
                'type': eval_item['type'],
                'total_score': eval_item['result']['total_score'],
                'breakdown': eval_item['result'].get('breakdown', [])
            })
        
        csv_content = generate_csv_report(csv_data)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=evaluations.csv"
            }
        )
    except Exception as e:
        print(f"Error generating CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
