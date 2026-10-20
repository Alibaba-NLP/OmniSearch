from llm_config import call_gpt 

class QAAgent:
    def __init__(self, model, headers, base_url):
        self.model = model
        self.headers = headers
        self.base_url = base_url
    
    def ask_gpt(self, messages, idx):
        success, idx, message, answer = call_gpt(
            self.model, messages, idx, self.headers, self.base_url
        )
            
        return success, idx, message, answer

