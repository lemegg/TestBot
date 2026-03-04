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
        You are an internal SOP Chatbot for 'The Affordable Organic Store'. 
        Your goal is to provide helpful, actionable answers based on the provided SOP context.

        USER QUERY: {query}

        STRICT JSON STRUCTURE:
        {{
          "answer": {{
            "summary": "direct answer to the user's question",
            "steps": ["step 1", "step 2", ...],
            "rules": ["policy 1", "policy 2", ...],
            "notes": ["tips or extra info"]
          }},
          "sources": [
            {{
              "sop": "Filename.pdf",
              "section": "Section Name"
            }}
          ]
        }}

        INSTRUCTIONS:
        1. Base your answer ONLY on the context provided below.
        2. If the context contains general information about the topic but not exact steps, summarize what is available to be helpful.
        3. If you find multiple related processes, explain the most relevant one for the user query.
        4. If there is absolutely NO relevant information in the context to answer the query, ONLY then set summary to "Information not found in SOPs" and leave all lists empty.
        5. Keep descriptions concise and formatted for a chat interface.

        CONTEXT:
        {context_str}
        """

        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
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
