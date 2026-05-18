import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class InterviewerAgent:
    def __init__(self, model_name="gemini-flash-latest"):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = model_name

    def generate_question(self, topic="general CS", difficulty="medium", context=""):
        prompt = f"""
        You are a Senior AI Technical Interviewer at a top tech company.
        
        Topic: {topic}
        Difficulty: {difficulty}
        Contextual Data: {context}
        
        Generate ONE challenging but fair technical interview question.
        
        Rules:
        1. Contextual: If context is provided, base your question on it. If not, use your vast general knowledge.
        2. Format: Return ONLY the question text.
        3. Variation: Ask about concepts, trade-offs, real-world scenarios, OR ask them to solve a coding problem. Let the topic dictate the type of question.
        4. No Answers: Do not provide the answer to the question.
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text.strip()
