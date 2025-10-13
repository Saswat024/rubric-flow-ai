from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import base64
from evaluators.flowchart import evaluate_flowchart
from evaluators.pseudocode import evaluate_pseudocode
from database import (
    create_user, verify_user, create_session, verify_session, 
    delete_session, get_user_email, save_evaluation, get_user_evaluations
)

app = FastAPI()

# Enable CORS for local React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "http://localhost:3000"],
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

@app.get("/api/evaluations")
async def api_get_evaluations(user_id: int = Depends(get_current_user)):
    """Get user's evaluation history"""
    try:
        evaluations = get_user_evaluations(user_id)
        return evaluations
    except Exception as e:
        print(f"Error fetching evaluations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
