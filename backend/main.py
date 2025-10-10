from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
from evaluators.flowchart import evaluate_flowchart
from evaluators.pseudocode import evaluate_pseudocode

app = FastAPI()

# Enable CORS for local React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Your Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PseudocodeRequest(BaseModel):
    code: str

class FlowchartRequest(BaseModel):
    image: str  # base64 encoded image

@app.post("/api/evaluate-flowchart")
async def api_evaluate_flowchart(request: FlowchartRequest):
    try:
        result = await evaluate_flowchart(request.image)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate-pseudocode")
async def api_evaluate_pseudocode(request: PseudocodeRequest):
    try:
        result = await evaluate_pseudocode(request.code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
