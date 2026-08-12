import requests
import time

workers=4
skip_lines = 0

LIMIT = 1000000000000 
retry_attempt = 10


def call_gpt(model, messages, idx, headers, base_url):
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

            r = requests.post(
                f"{base_url.rstrip('/')}/chat/completions",
                json=data,
                headers=headers
            )
            resp = r.json()

            if r.status_code != 200:
                print('请求失败，重试中！')
                print(resp)
                continue

            if 'choices' in resp and resp['choices'][0].get('finish_reason') in ['content_filter', 'ResponsibleAIPolicyViolation']:
                print('内容不符合策略要求，返回空结果')
                return (False, idx, "", "", 0, 0, 0)
            message = resp['choices'][0]['message']
            answer = message['content']

            return (True, idx, message, answer)

        except Exception as e:
            print(e)
            print('发生异常，重试中！')
            time.sleep(1)  # 等待一段时间再重试
            continue

