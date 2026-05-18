import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add the project root to sys.path
# This handles cases where you run from the root OR from within the backend folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from backend.rag_manager import RAGManager
    from backend.agents.explainer import ExplainerAgent
    from backend.agents.interviewer import InterviewerAgent
    from backend.agents.evaluator import EvaluatorAgent
except ModuleNotFoundError:
    from rag_manager import RAGManager
    from agents.explainer import ExplainerAgent
    from agents.interviewer import InterviewerAgent
    from agents.evaluator import EvaluatorAgent

# Load Environment Variables
load_dotenv()

app = FastAPI(title="AI Technical Interview Expert Backend")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG and Agents
rag_manager = RAGManager() # Uses dynamic path resolution to find data/kb.txt
explainer_agent = ExplainerAgent(model_name="gemini-flash-latest")
interviewer_agent = InterviewerAgent(model_name="gemini-flash-latest")
evaluator_agent = EvaluatorAgent(model_name="gemini-flash-latest")

class UserQuery(BaseModel):
    query: str

class InterviewRequest(BaseModel):
    topic: str
    difficulty: str = "medium"

class EvaluationRequest(BaseModel):
    question: str
    user_answer: str

@app.get("/")
def read_root():
    return {"message": "AI Technical Interview Expert API is live!"}

@app.post("/explain")
def get_explanation(user_query: UserQuery):
    try:
        context = rag_manager.search(user_query.query)
        answer = explainer_agent.get_structured_answer(user_query.query, context=context)
        return {"query": user_query.query, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview/start")
def start_interview(request: InterviewRequest):
    try:
        # Step 1: Search KB for context
        context = rag_manager.search(request.topic)
        
        # Step 2: Generate Question
        question = interviewer_agent.generate_question(
            topic=request.topic, 
            difficulty=request.difficulty,
            context=context
        )
        
        return {"topic": request.topic, "question": question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview/evaluate")
def evaluate_interview(request: EvaluationRequest):
    try:
        # Step 1: Search KB for truth context
        context = rag_manager.search(request.question)
        
        # Step 2: Evaluate
        evaluation = evaluator_agent.evaluate_response(
            question=request.question,
            user_answer=request.user_answer,
            context=context
        )
        return {"evaluation": evaluation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
