import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from config import Config

class VectorStore:
    def __init__(self):
        self.persist_directory = Config.CHROMA_PATH
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # --- FIX: Explicitly disable telemetry to stop the errors ---
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(name="agentic_ai_docs")

    def create_collection(self, force: bool = False):
        if force:
            try:
                self.client.delete_collection("agentic_ai_docs")
            except:
                pass
            self.collection = self.client.create_collection(name="agentic_ai_docs")
        return True

    def add_documents(self, chunks: List[Dict]):
        if not chunks: return False
        
        ids = [f"doc_{c['chunk_index']}" for c in chunks]
        texts = [c['text'] for c in chunks]
        metadatas = [{"page": c['page'], "chunk_index": c['chunk_index']} for c in chunks]

        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            self.collection.upsert(
                ids=ids[i:i+batch_size],
                documents=texts[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )
        return True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                formatted_results.append({
                    'text': doc,
                    'metadata': meta,
                    'chunk_index': meta['chunk_index'],
                    'page': meta['page'],
                    'score': 1 - (results['distances'][0][i] if results['distances'] else 0)
                })
        
        # Sort by book order so the text flows naturally
        formatted_results.sort(key=lambda x: x['chunk_index'])
        
        return formatted_results