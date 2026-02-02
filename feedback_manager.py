import json
import os
from typing import List, Dict, Optional
from config import Config
import difflib

class FeedbackManager:
    def __init__(self):
        self.file_path = Config.FEEDBACK_FILE
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        self.history = self._load_history()

    def _load_history(self) -> List[Dict]:
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except:
            return []

    def store_feedback(self, query: str, bot_response: str, feedback_type: str, instruction: Optional[str] = None):
        if not query: return
        
        entry = {
            "query": query,
            "bot_response": bot_response,
            "feedback_type": feedback_type,
            "instruction": instruction
        }
        
        # Remove old duplicate instructions for cleanliness
        self.history = [h for h in self.history if h['query'].strip().lower() != query.strip().lower()]
        self.history.append(entry)
        
        with open(self.file_path, 'w') as f:
            json.dump(self.history, f, indent=2)

    def get_instruction_for_query(self, query: str) -> Optional[str]:
        if not query: return None
        
        # 1. Exact Match (Fast)
        for entry in reversed(self.history):
            if entry['query'].strip().lower() == query.strip().lower() and entry.get('instruction'):
                return entry['instruction']
        
        # 2. Smart Fuzzy Match
        # If user learned "List authors" and asks "Please list authors", match it.
        query_words = set(query.lower().split())
        best_match = None
        best_ratio = 0.0
        
        for entry in reversed(self.history):
            if not entry.get('instruction'): continue
            
            entry_words = set(entry['query'].lower().split())
            
            # Intersection score
            overlap = len(query_words.intersection(entry_words))
            if overlap == 0: continue
            
            ratio = overlap / len(entry_words) # How much of the learned query is in the new query
            
            if ratio > 0.6 and ratio > best_ratio:
                best_ratio = ratio
                best_match = entry['instruction']
        
        return best_match
        
    def get_stats(self):
        total = len(self.history)
        instructions = len([x for x in self.history if x.get('instruction')])
        return {"total": total, "instructions_learned": instructions}