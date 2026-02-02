import pandas as pd
import logging
from io import StringIO

class TableParser:
    def detect_and_answer(self, context_text: str, query: str) -> str:
        # 1. Identify table-like structures
        lines = context_text.split('\n')
        table_lines = [line for line in lines if "|" in line and len(line.split("|")) > 2]
        
        if not table_lines:
            return None

        # 2. Check query intent
        triggers = ["table", "list", "compare", "data", "versus", "vs", "difference"]
        if not any(t in query.lower() for t in triggers):
            return None

        try:
            # 3. Clean and Parse
            clean_lines = [l for l in table_lines if "---" not in l]
            
            rows = [row.strip().split('|') for row in clean_lines]
            # Clean empty cells
            rows = [[c.strip() for c in row if c.strip()] for row in rows]
            
            if len(rows) < 2: return None
                
            headers = rows[0]
            data = rows[1:]
            
            df = pd.DataFrame(data, columns=headers)
            return f"**Table Found:**\n\n{df.to_markdown(index=False)}"
        except Exception:
            return None