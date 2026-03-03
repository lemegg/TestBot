import google.generativeai as genai
from typing import List, Dict, Any
import json
from app.core.config import settings

class Generator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.MODEL_NAME)

    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not context_chunks:
            return {
                "answer": {
                    "summary": "I'm sorry, I couldn't find any relevant information in the SOPs to answer your question.",
                    "steps": [],
                    "rules": [],
                    "notes": []
                },
                "sources": []
            }

        context_str = ""
        for i, chunk in enumerate(context_chunks):
            context_str += f"--- CONTEXT {i+1} ---\n"
            context_str += f"SOP: {chunk['sop_name']}\n"
            context_str += f"Section: {chunk['section']}\n"
            context_str += f"Content: {chunk['text']}\n\n"

        prompt = f"""
        You are an internal chatbot assistant. Answer the user query based ONLY on the provided SOP context.
        You MUST output your response in STRICT JSON format.

        JSON STRUCTURE:
        {{
          "answer": {{
            "summary": "short 1–2 line direct answer",
            "steps": ["step 1", "step 2", ...],
            "rules": ["policy rule 1", "policy rule 2", ...],
            "notes": ["extra useful info or edge cases"]
          }},
          "sources": [
            {{
              "sop": "SOP filename",
              "section": "Section name"
            }}
          ]
        }}

        STRICT RULES:
        1. Answer ONLY from the provided context.
        2. Be concise. No long paragraphs.
        3. Use 'steps' for any process or sequence of actions.
        4. Use 'rules' for mandatory policies or constraints.
        5. Use 'notes' for extra context or tips.
        6. If a field (steps, rules, notes) has no content, return an empty array [].
        7. Only include 'sources' that were actually used to form the answer.
        8. If you don't know the answer, set summary to "Information not found in SOPs" and all arrays to [].

        CONTEXT:
        {context_str}

        USER QUERY:
        {query}
        """

        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            print(f"AI RAW RESPONSE: {response.text}")
            return json.loads(response.text.strip())
        except Exception as e:
            print(f"AI Generation Error: {e}")
            # Fallback for parsing errors or API issues
            return {
                "answer": {
                    "summary": f"I encountered an error while processing your request: {str(e)}",
                    "steps": [],
                    "rules": [],
                    "notes": ["Please try rephrasing your question or check the logs for more details."]
                },
                "sources": []
            }
