import google.generativeai as genai
from typing import List, Dict, Optional
import PyPDF2
from pathlib import Path
from config import Config
from vector_store import VectorStore

class RAGEngine:
    def __init__(self):
        self.config = Config
        self.vector_store = VectorStore()
        genai.configure(api_key=self.config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(self.config.MODEL_NAME)
    
    def initialize_database(self, pdf_path: str, force: bool = False):
        if not Path(pdf_path).exists(): return False
        self.vector_store.create_collection(force=force)
        
        reader = PyPDF2.PdfReader(pdf_path)
        full_text = ""
        page_map = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                page_map.append((len(full_text), i + 1))
                full_text += text + "\n"
        
        chunks = []
        start = 0
        idx = 0
        while start < len(full_text):
            end = start + self.config.CHUNK_SIZE
            chunk_text = full_text[start:end]
            page_num = 1
            for pos, p_num in page_map:
                if start >= pos: page_num = p_num
                else: break
            
            chunks.append({
                "chunk_index": idx, "text": chunk_text,
                "page": page_num, "source": "PDF"
            })
            start += (self.config.CHUNK_SIZE - self.config.CHUNK_OVERLAP)
            idx += 1
            
        self.vector_store.add_documents(chunks)
        return True

    def answer_query(self, query: str, context_chunks: List[Dict], instruction: Optional[str] = None) -> str:
        if not context_chunks:
            return "I couldn't find any relevant information in the document."

        # Format context with Page Numbers
        context_str = ""
        for c in context_chunks:
            context_str += f"\n--- [PAGE {c['metadata']['page']}] ---\n{c['text']}\n"
        
        # --- DYNAMIC PROMPT LOGIC ---
        
        base_instruction = """You are an Agentic AI assistant. Your goal is to answer based ONLY on the provided context."""
        
        # Check User Intent
        is_list_request = any(w in query.lower() for w in ['list', 'enumerate', 'titles'])
        is_detailed_request = any(w in query.lower() for w in ['explain', 'describe', 'details', 'what are', 'how'])
        
        mode_instruction = ""
        
        if instruction:
            # 1. HIGHEST PRIORITY: Learned Feedback
            # If the user previously taught the bot a rule, we follow that EXACTLY.
            mode_instruction = f"\n🚨 CRITICAL USER RULE: The user previously corrected this query with: '{instruction}'. YOU MUST FOLLOW THIS RULE ABOVE ALL ELSE."
        
        elif is_list_request and not is_detailed_request:
            # 2. "List" Query (e.g., "List the benefits") -> Titles Only
            mode_instruction = """
            \nMODE: CONCISE LIST
            - Provide ONLY the names/titles of the items.
            - Do NOT include the full descriptions or paragraphs.
            - Format as a clean bulleted list.
            """
            
        else:
            # 3. Default / "What are" Query -> Full Details
            mode_instruction = """
            \nMODE: DETAILED BREAKDOWN
            - Provide the full answer including Titles AND their Descriptions.
            - Do not dump text. Use a point-by-point format (e.g., **Title**: Description).
            - Ensure all details from the text are included.
            """

        final_prompt = f"""{base_instruction}
        
        {mode_instruction}
        
        CONTEXT FROM DOCUMENT:
        {context_str}
        
        USER QUESTION: {query}
        
        FINAL CHECKS:
        1. Cite [Page X] for every key point.
        2. Do not hallucinate.
        """
        
        try:
            response = self.model.generate_content(final_prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"