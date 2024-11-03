import requests
import time

workers=4
skip_lines = 0

LIMIT = 1000000000000 
retry_attempt = 10


#调用gpt的api回答问题，包含了违规检查和内容过滤错误。但不是官方的api，其中的一些参数可能要修改成openai的官方参数规范

def call_gpt(model, messages, idx, headers ):
    # 准备请求数据，包括模型、对话信息等参数
    data = {
        "model": model,
        "messages": messages,
        "n": 1,  # 回答数量
        "max_tokens": 4096
    }
    
    answer = None
    while answer is None:
        try:
            # 发送 POST 请求到中转 API
            r = requests.post(
                #'https://api.chatanywhere.tech/v1/chat/completions', 
                'https://api.openai.com/v1/chat/completions',
                json=data,
                headers=headers
            )
            resp = r.json()

            # 检查 API 响应的状态码与内容
            if r.status_code != 200:
                print('请求失败，重试中！')
                print(resp)
                continue
            
            # 检查内容策略的相关代码
            if 'choices' in resp and resp['choices'][0].get('finish_reason') in ['content_filter', 'ResponsibleAIPolicyViolation']:
                print('内容不符合策略要求，返回空结果')
                return (False, idx, "", "", 0, 0, 0)

            # 提取 tokens 信息和生成的回答
            #total_tokens = resp['usage']['total_tokens']
            #prompt_tokens = resp['usage']['prompt_tokens']
            #completion_tokens = resp['usage']['completion_tokens']
            message = resp['choices'][0]['message']
            answer = message['content']

            return (True, idx, message, answer)

        except Exception as e:
            print(e)
            print('发生异常，重试中！')
            time.sleep(1)  # 等待一段时间再重试
            continue

