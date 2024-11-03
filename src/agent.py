from llm_config import call_gpt 

#负责处理问题并调用GPT模型生成回答
class QAAgent:
    def __init__(self, model, headers):
        #super().__init__()
        self.model = model
        self.headers = headers
        #self.gpt4v_used_tokens_list = []
        #self.qwen_used_tokens_list = []
    
    def ask_gpt(self, messages, idx):
        success, idx, message, answer = call_gpt(
            self.model, messages, idx, self.headers
        )
            
        return success, idx, message, answer

