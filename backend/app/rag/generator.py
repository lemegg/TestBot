import google.generativeai as genai
from typing import List, Dict, Any
import json
import re
from app.core.config import settings

class Generator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use explicit model name from settings
        self.model_name = settings.MODEL_NAME
        self.model = genai.GenerativeModel(self.model_name)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Robustly extract JSON from text, handling markdown blocks or extra text."""
        # Clean the text
        text = text.strip()
        
        # 1. Try finding JSON within markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL | re.IGNORECASE)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 2. Try finding anything that looks like a JSON object using balanced braces
        # This is more robust than simple regex for 'Extra data' errors
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_candidate = text[start_idx:end_idx + 1]
                return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass
        
        # 3. Last ditch: clean common LLM garbage and try direct parse
        cleaned_text = text.replace('```json', '').replace('```', '').strip()
        return json.loads(cleaned_text)

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
        2. If the context contains URLs or links to sheets/documents, ALWAYS include them in your answer as clickable markdown links (e.g., [Link Name](https://...)).
        3. If the context contains general information about the topic but not exact steps, summarize what is available to be helpful.
        4. If you find multiple related processes, explain the most relevant one for the user query.
        5. If there is absolutely NO relevant information in the context to answer the query, ONLY then set summary to "Information not found in SOPs" and leave all lists empty.
        6. Keep descriptions concise and formatted for a chat interface.

        CONTEXT:
        {context_str}
        """

        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            raw_text = response.text.strip()
            return self._extract_json(raw_text)
        except Exception as e:
            print(f"AI Generation/Parse Error: {e}")
            # Fallback for parsing errors or API issues
            return {
                "answer": {
                    "summary": f"I encountered an error while processing your request. Please try rephrasing your question.",
                    "steps": [],
                    "rules": [],
                    "notes": [f"Debug info: {str(e)}"]
                },
                "sources": []
            }
