from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import base64
import json
from evaluators.flowchart import evaluate_flowchart
from evaluators.pseudocode import evaluate_pseudocode
from evaluators.algorithm import evaluate_algorithm
from parsers.document_parser import parse_document
from export.report_generator import generate_pdf_report, generate_csv_report, generate_comparison_pdf_report
from database import (
    create_user, verify_user, create_session, verify_session, 
    delete_session, get_user_email, save_evaluation, get_user_evaluations,
    save_comparison, get_user_comparisons, get_comparison_by_id,
    find_similar_problem, create_problem, update_problem_cfg, get_problem_by_id,
    save_solution, get_reference_solution, get_problem_solutions, get_db_connection
)
from analyzers.cfg_generator import pseudocode_to_cfg, flowchart_to_cfg, cfg_to_dict
from analyzers.problem_analyzer import analyze_problem
from analyzers.cfg_comparator import compare_cfgs
from analyzers.cfg_visualizer import cfg_to_mermaid
from analyzers.cfg_canonicalizer import canonicalize_cfg, calculate_cfg_similarity

app = FastAPI()

# Enable CORS for local React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

class SolutionInput(BaseModel):
    type: str  # 'flowchart' or 'pseudocode'
    content: str  # base64 for flowchart, text for pseudocode

class ComparisonRequest(BaseModel):
    problem_statement: str
    solution1: SolutionInput
    solution2: SolutionInput

# Dependency to get current user from token
async def get_current_user(authorization: Optional[str] = Header(None)) -> int:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    user_id = verify_session(token)
    
    if not user_id:
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

@app.post("/api/compare-solutions")
async def api_compare_solutions(request: ComparisonRequest, user_id: int = Depends(get_current_user)):
    """Compare two solutions using CFG analysis"""
    print("\n=== SOLUTION COMPARISON REQUEST RECEIVED ===")
    try:
        print(f"User ID: {user_id}")
        print(f"Problem: {request.problem_statement[:100]}...")
        print(f"Solution 1 type: {request.solution1.type}")
        print(f"Solution 2 type: {request.solution2.type}")
        
        # Analyze problem statement
        print("Analyzing problem...")
        problem_analysis = await analyze_problem(request.problem_statement)
        
        # Generate CFGs for both solutions
        print("Generating CFG for Solution 1...")
        if request.solution1.type == 'flowchart':
            cfg1 = await flowchart_to_cfg(request.solution1.content)
        else:
            cfg1 = await pseudocode_to_cfg(request.solution1.content)
        
        print("Generating CFG for Solution 2...")
        if request.solution2.type == 'flowchart':
            cfg2 = await flowchart_to_cfg(request.solution2.content)
        else:
            cfg2 = await pseudocode_to_cfg(request.solution2.content)
        
        # Compare CFGs
        print("Comparing solutions...")
        comparison_result = await compare_cfgs(cfg1, cfg2, problem_analysis)
        
        # Generate Mermaid visualizations
        print("Generating visualizations...")
        cfg1_mermaid = cfg_to_mermaid(cfg1, "Solution 1")
        cfg2_mermaid = cfg_to_mermaid(cfg2, "Solution 2")
        
        # Convert CFGs to dict for storage
        cfg1_dict = cfg_to_dict(cfg1)
        cfg2_dict = cfg_to_dict(cfg2)
        
        # Save to database
        overall_scores = {
            'solution1': comparison_result['solution1_score'],
            'solution2': comparison_result['solution2_score']
        }
        
        comparison_id = save_comparison(
            user_id=user_id,
            problem_statement=request.problem_statement,
            solution1_type=request.solution1.type,
            solution1_content=request.solution1.content,
            solution2_type=request.solution2.type,
            solution2_content=request.solution2.content,
            cfg1_json=json.dumps(cfg1_dict),
            cfg2_json=json.dumps(cfg2_dict),
            comparison_result=comparison_result,
            winner=comparison_result['winner'],
            overall_scores=overall_scores
        )
        
        print(f"Comparison saved with ID: {comparison_id}")
        
        # Return complete result
        return {
            'comparison_id': comparison_id,
            'winner': comparison_result['winner'],
            'solution1_score': comparison_result['solution1_score'],
            'solution2_score': comparison_result['solution2_score'],
            'comparison': comparison_result['comparison'],
            'overall_analysis': comparison_result['overall_analysis'],
            'recommendations': comparison_result['recommendations'],
            'cfg1': cfg1_dict,
            'cfg2': cfg2_dict,
            'cfg1_mermaid': cfg1_mermaid,
            'cfg2_mermaid': cfg2_mermaid,
            'problem_analysis': problem_analysis
        }
    except Exception as e:
        print(f"\n!!! ERROR in solution comparison: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/comparisons")
async def api_get_comparisons(user_id: int = Depends(get_current_user)):
    """Get user's comparison history"""
    try:
        comparisons = get_user_comparisons(user_id)
        return comparisons
    except Exception as e:
        print(f"Error fetching comparisons: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/comparison/{comparison_id}")
async def api_export_comparison(comparison_id: int, user_id: int = Depends(get_current_user)):
    """Export comparison as PDF"""
    try:
        comparison = get_comparison_by_id(comparison_id, user_id)
        
        if not comparison:
            raise HTTPException(status_code=404, detail="Comparison not found")
        
        user_email = get_user_email(user_id)
        
        # Generate PDF
        pdf_bytes = generate_comparison_pdf_report(comparison, user_email)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=comparison_{comparison_id}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating comparison PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


class ProblemUploadRequest(BaseModel):
    problem_statement: str

class ReferenceSolutionRequest(BaseModel):
    problem_id: int
    solution_type: str
    solution_content: str

class EvaluateSolutionRequest(BaseModel):
    problem_id: int
    solution_type: str
    solution_content: str


@app.post("/api/upload-problem")
async def api_upload_problem(request: ProblemUploadRequest, user_id: int = Depends(get_current_user)):
    """Upload or find existing problem"""
    try:
        similar = find_similar_problem(request.problem_statement)
        
        if similar:
            reference = get_reference_solution(similar['id'])
            return {
                "status": "found",
                "problem_id": similar['id'],
                "problem_statement": similar['problem_statement'],
                "bottom_line_cfg": similar['bottom_line_cfg'],
                "reference_solution_exists": reference is not None,
                "similarity_score": similar['similarity_score']
            }
        
        problem_id = create_problem(request.problem_statement)
        return {
            "status": "new_problem",
            "problem_id": problem_id,
            "problem_statement": request.problem_statement,
            "bottom_line_cfg": None,
            "reference_solution_exists": False,
            "similarity_score": 0
        }
    except Exception as e:
        print(f"Error uploading problem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fetch-reference-solution/{problem_id}")
async def api_fetch_reference(problem_id: int, user_id: int = Depends(get_current_user)):
    """Fetch reference solution for a problem"""
    try:
        problem = get_problem_by_id(problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        reference = get_reference_solution(problem_id)
        
        if not reference:
            return {"exists": False}
        
        mermaid = cfg_to_mermaid(reference['cfg_json'], "Reference Solution")
        
        return {
            "exists": True,
            "solution_type": reference['solution_type'],
            "solution_content": reference['solution_content'],
            "bottom_line_cfg": problem['bottom_line_cfg'],
            "mermaid_diagram": mermaid,
            "optimal_complexity": {
                "time": problem['optimal_time_complexity'],
                "space": problem['optimal_space_complexity']
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching reference: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-reference-solution")
async def api_upload_reference(request: ReferenceSolutionRequest, user_id: int = Depends(get_current_user)):
    """Upload reference solution and generate bottom-line CFG"""
    try:
        problem = get_problem_by_id(request.problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Generate CFG
        if request.solution_type == 'flowchart':
            cfg = await flowchart_to_cfg(request.solution_content)
        else:
            cfg = await pseudocode_to_cfg(request.solution_content)
        
        # Canonicalize to bottom-line CFG
        bottom_line_cfg = await canonicalize_cfg(cfg, problem['problem_statement'])
        
        # Extract complexity from canonicalized CFG
        time_complexity = bottom_line_cfg.get('time_complexity', 'O(n)')
        space_complexity = bottom_line_cfg.get('space_complexity', 'O(1)')
        
        # Update problem with bottom-line CFG
        update_problem_cfg(request.problem_id, bottom_line_cfg, time_complexity, space_complexity)
        
        # Save reference solution
        cfg_dict = cfg_to_dict(cfg)
        save_solution(request.problem_id, request.solution_type, request.solution_content, 
                     cfg_dict, is_reference=True, user_id=user_id)
        
        mermaid = cfg_to_mermaid(bottom_line_cfg, "Bottom-Line CFG")
        
        return {
            "success": True,
            "problem_id": request.problem_id,
            "bottom_line_cfg": bottom_line_cfg,
            "mermaid_diagram": mermaid,
            "complexity_analysis": {
                "time": time_complexity,
                "space": space_complexity
            }
        }
    except Exception as e:
        print(f"Error uploading reference: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate-solution")
async def api_evaluate_solution(request: EvaluateSolutionRequest, user_id: int = Depends(get_current_user)):
    """Evaluate user solution against bottom-line CFG"""
    try:
        problem = get_problem_by_id(request.problem_id)
        if not problem or not problem['bottom_line_cfg']:
            raise HTTPException(status_code=400, detail="No reference solution available for this problem")
        
        # Generate CFG from user solution
        if request.solution_type == 'flowchart':
            user_cfg = await flowchart_to_cfg(request.solution_content)
        else:
            user_cfg = await pseudocode_to_cfg(request.solution_content)
        
        user_cfg_dict = cfg_to_dict(user_cfg)
        
        # Compare with bottom-line CFG
        evaluation = await calculate_cfg_similarity(user_cfg_dict, problem['bottom_line_cfg'])
        
        # Save user solution
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, evaluation_score FROM solutions WHERE problem_id = ? AND user_id = ? AND is_reference_solution = 0",
                (request.problem_id, user_id)
            )
            existing = cursor.fetchone()
            if existing and existing[1] and existing[1] >= evaluation["total_score"]:
                solution_id = existing[0]
            elif existing:
                cursor.execute(
                    "UPDATE solutions SET solution_content = ?, cfg_json = ?, evaluation_score = ?, evaluation_result = ? WHERE id = ?",
                    (request.solution_content[:5000], json.dumps(user_cfg_dict), evaluation["total_score"], json.dumps(evaluation), existing[0])
                )
                conn.commit()
                solution_id = existing[0]
            else:
                solution_id = save_solution(
                    request.problem_id, request.solution_type, request.solution_content,
                    user_cfg_dict, is_reference=False, user_id=user_id,
                    evaluation_score=evaluation["total_score"], evaluation_result=evaluation
                )

        # Generate visualizations
        user_mermaid = cfg_to_mermaid(user_cfg_dict, "Your Solution")
        reference_mermaid = cfg_to_mermaid(problem['bottom_line_cfg'], "Reference Solution")
        
        return {
            "evaluation_id": solution_id,
            "total_score": evaluation['total_score'],
            "breakdown": evaluation['breakdown'],
            "cfg_comparison": {
                "user_cfg": user_cfg_dict,
                "reference_cfg": problem['bottom_line_cfg'],
                "differences": evaluation.get('differences', []),
                "missing_paths": evaluation.get('missing_paths', []),
                "extra_paths": evaluation.get('extra_paths', [])
            },
            "mermaid_diagrams": {
                "user": user_mermaid,
                "reference": reference_mermaid
            },
            "recommendations": evaluation.get('recommendations', [])
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error evaluating solution: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/problems")
async def api_get_problems(user_id: int = Depends(get_current_user)):
    """Get all problems with statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.problem_statement, p.problem_category, p.created_at,
                       COUNT(s.id) as solution_count,
                       AVG(s.evaluation_score) as avg_score
                FROM problems p
                LEFT JOIN solutions s ON p.id = s.problem_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT 50
            """)
            results = cursor.fetchall()
            
            return [{
                'id': r[0],
                'problem_statement': r[1][:200] + '...' if len(r[1]) > 200 else r[1],
                'category': r[2],
                'created_at': r[3],
                'solution_count': r[4] or 0,
                'avg_score': round(r[5], 1) if r[5] else None
            } for r in results]
    except Exception as e:
        print(f"Error fetching problems: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/problems/{problem_id}")
async def api_delete_problem(problem_id: int, user_id: int = Depends(get_current_user)):
    """Delete a problem and its associated solutions"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM solutions WHERE problem_id = ?", (problem_id,))
            cursor.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
            conn.commit()
            return {"success": True, "message": "Problem deleted"}
    except Exception as e:
        print(f"Error deleting problem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
