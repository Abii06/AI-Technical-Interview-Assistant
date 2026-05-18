import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class ExplainerAgent:
    def __init__(self, model_name="gemini-flash-latest"):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model_name = model_name

    def get_structured_answer(self, query, context=""):
        prompt = f"""
        You are an AI Technical Interview Expert.
        
        Context:
        {context}
        
        Question:
        {query}
        
        Provide a structured answer in the following format ONLY:
        
        🟢 Simple Explanation:
        (A parent-level explanation using easy analogies)
        
        🔵 Technical Explanation:
        (Key concepts, components, and how it works theoretically)
        
        🟡 Interview Answer:
        (A formal, precise answer as one would say in a technical round)
        
        🟣 Real-world Example:
        (A practical application in industry or modern systems)
        
        💻 Code Implementation / Solution:
        (If the question involves an algorithm, data structure, or problem solving, provide clean, well-commented code here. If not applicable, just say "No code required for this concept.")
        
        Rules:
        1. Accuracy: Base your technical answer on the provided context where possible. If the context is insufficient or empty, use your extensive general knowledge to answer ANY academic, coding, or problem-solving question accurately.
        2. Clarity: Avoid jargon in the Simple Explanation.
        3. Professionalism: Be sharp and confident in the Interview Answer.
        4. Consistency: Ensure all layers are about the same concept.
        """
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text
