from typing import List, Dict

class ConversationMemory:
    def __init__(self, max_messages: int = 25):
        self.history : List[Dict] = []
        self.max_messages = max_messages
    
    def add(self, role:str, content: str):
        self.history.append({
            "role":role,
            "content":content
        })

        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]
    
    def get(self)->List[Dict]:
        return self.history
    
    def clear(self):
        self.history =[]
    
    def format_for_prompt(self)->str:
        formatted = ""
        for msg in self.history:
            formatted += f"{msg['role'].upper()}:{msg['content']}\n"
        return formatted