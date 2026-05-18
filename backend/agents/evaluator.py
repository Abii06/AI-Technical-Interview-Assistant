import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class EvaluatorAgent:
    def __init__(self, model_name="gemini-flash-latest"):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = model_name

    def evaluate_response(self, question, user_answer, context=""):
        prompt = f"""
        You are a Top-Tier AI Technical Interview Evaluator.
        
        Question: {question}
        User's Answer: {user_answer}
        
        Reference Technical Data:
        {context}
        
        Evaluate the user's answer strictly based on:
        1. Technical Accuracy (Is the concept explained correctly, or is the code solution valid and optimal?)
        2. Completeness (Are key points covered, or are edge cases handled in code?)
        3. Professionalism (Is it structured like an interview answer, or is the code clean and well-commented?)
        
        Use the Reference Technical Data if available. If it's empty or insufficient, use your vast general knowledge to evaluate the answer accurately.
        
        Return your evaluation in this format ONLY:
        
        📊 Score: (0-10)
        
        ❌ Mistakes:
        (Bullet points of any technical errors or key omissions)
        
        📈 Improvements:
        (Specific advice on how to make the answer better)
        
        🤔 Recommended Follow-up:
        (What question should the user study next?)
        
        Do not provide anything else.
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text.strip()
