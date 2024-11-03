from mimetypes import guess_type
import base64
import requests,json
import os
from serpapi import GoogleSearch
import time
from io import BytesIO
from PIL import Image

API_KEY = "e9ce913a9f240d0046160382d8ac1c8f4fc124e63a179d238aa61f1a53789a2b"
retry_attempt=3
# Function to encode a local image into data URL将本地图像转换为Data URL格式 
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

# pip3 install serpapi
def search_text_by_text(text):
    params = {
        "engine": "google",
        "q": text,
        "api_key": API_KEY,
        #"hl": "zh-CN",
        #"gl": "CN",
        "num": 5
    }

    for i in range(retry_attempt):
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            #print(results)
            #print("-----")
            organic_results = results["organic_results"]
            #print(organic_results)
            return organic_results

        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            if i < retry_attempt - 1:
                time.sleep(2)  # 等待2秒后重试
            else:
                print("All retries failed.")
                return {}
            
def search_image_by_text(text, retry_attempt=3):
    params = {
        "engine": "google_images",
        "q": text,
        #"hl": "zh-CN",
        #"gl": "CN",
        "api_key": API_KEY 
        
    }

    for i in range(retry_attempt):
        try:
            search = GoogleSearch(params)
            results = search.get_dict()  # 获取图片搜索结果
            organic_results = results["images_results"]
            print(organic_results[0])
            return organic_results[0]

        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            if i < retry_attempt - 1:
                time.sleep(2)  # 等待2秒后重试
            else:
                print("All retries failed.")
                return {}


'''def search_image_by_image_url(input_url):

  print(input_url)
  params = {
        "engine": "google_reverse_image",
        "image_url": input_url,
        "hl": "zh-CN",
        "gl": "CN",
        "api_key": API_KEY
    }

  for i in range(retry_attempt):
        try:
            search = GoogleSearch(params)
            results = search.get_dict()["knowledge_graph"]  # 获取图片搜索结果
            print("Image search success!")
            print(results)
            return results

        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            if i < retry_attempt - 1:
                time.sleep(2)  # 等待2秒后重试
            else:
                print("All retries failed.")
                return {}'''

def search_image_by_image_url(input_url):
    print(f"Searching for image by URL: {input_url}")
    
    params = {
        "engine": "google_reverse_image",
        "image_url": input_url,
        "hl": "zh-CN",
        "gl": "CN",
        "api_key": API_KEY
    }

    for i in range(retry_attempt):
        try:
            search = GoogleSearch(params)
            results  = search.get_dict()  # 获取完整的返回结果
            #print(results)
            return results
            '''if "knowledge_graph" in result_dict:
                results = result_dict
                #results = result_dict["knowledge_graph"]
                print("Image search success (using knowledge_graph)!")
                print(results)
                #print(result_dict)
                #for item in results['header_images']:
                    #image_url = item['source']
                    #print(image_url)
                return results
            elif "image_results" in result_dict:
                results = result_dict
                #results = result_dict["image_results"]
                print("Image search success (using image_results)!")
                #print(results)
                #print(result_dict)
                return results
            else:
                # 如果没有 knowledge_graph 和 image_results，打印完整的响应
                print(f"Attempt {i+1} failed: No 'knowledge_graph' or 'image_results' found in response.")
                print("Full response:", result_dict)'''
            

        except Exception as e:
            print(f"Attempt {i+1} failed due to error: {e}")
            # 打印详细的错误信息，特别是 SSL 错误信息
            if "SSLError" in str(e):
                print("SSL error encountered. This could be due to network issues or SSL library compatibility.")
            elif "ConnectionError" in str(e):
                print("Network connection error. Retrying may help if this is a temporary network issue.")
            
        # 如果不是最后一次重试，等待2秒再尝试
        if i < retry_attempt - 1:
            time.sleep(2)  # 等待2秒后重试
        else:
            print("All retries failed. Returning empty result.")
            return {}

def parse_image_search_result_by_text(search_result, save_path, idx, conversation_num):
    search_images = []
    search_texts = []
        
    # 获取原始图片 URL
    image_url = search_result['thumbnail']
    try:
        # 下载图像
        response = requests.get(image_url)
        response.raise_for_status()  # 检查请求是否成功
        image_bytes = BytesIO(response.content)
        image = Image.open(image_bytes)
        
        # 保存图像
        save_image_path = os.path.join(save_path, '{}_{}_{}.png'.format(idx, conversation_num, search_result.get("position", "0")))
        image.save(save_image_path, format='PNG')
        
        # 添加图像路径和描述到列表中
        search_images.append((image_url, save_image_path))
        search_texts.append(search_result.get('title', ''))  # 获取图像的标题和来源

    except Exception as e:
        print(f"Failed to download or save image from {image_url}: {e}")
        #continue

    return search_images, search_texts

def parse_image_search_result_by_image(search_results, save_path, idx, conversation_num):
    search_images = []
    search_texts = []
    

    #if "knowledge_graph" in search_results:
    if "knowledge_graph" in search_results and 'header_images' in search_results["knowledge_graph"]:
        search_result = search_results["knowledge_graph"]
        # 遍历 search_result 
        #if "header_images" in search_result:
        #if 'header_images' in search_result:
        for item in search_result['header_images']:
            
            # 获取 'source' 作为图片的 URL
            image_url = item['source']
            
            try:
                # 下载图像
                response = requests.get(image_url)
                response.raise_for_status()  # 检查请求是否成功
                image_bytes = BytesIO(response.content)
                image = Image.open(image_bytes)
                
                # 保存图像
                save_image_path = os.path.join(save_path, '{}_{}_{}.png'.format(idx, conversation_num, "header"))
                image.save(save_image_path, format='PNG')
                
                # 组合 'title' 和 'description' 作为文本
                image_text = search_result.get('title', '') + ": " + search_result.get('description', '')
                #image_text = search_result['description']

                # 添加图像路径和描述到列表中
                search_images.append((image_url, save_image_path))
                search_texts.append(image_text)

            except Exception as e:
                print(f"Failed to download or save image from {image_url}: {e}")
                continue

    elif "image_results" in search_results:
        #results = result_dict
        search_result = search_results['image_results']

        for item in search_result:
            try:
                image_text=item['snippet']
                search_texts.append(image_text)
            except Exception as e:
                print("Failed to add text to search_text")
                continue
    else:
                # 如果没有 knowledge_graph 和 image_results，打印完整的响应
                print("Attempt failed: No 'knowledge_graph' or 'image_results' found in response.")
                print("Full response:",search_results )            
    #print(search_images)
    #print(search_texts)
    return search_images, search_texts

def fine_search(query, search_type, save_path, dataset_name, idx, conversation_num):
    if search_type == 'text_search_text':
        search_result = search_text_by_text(query)
        search_texts = []
        
        for item in search_result:
            text_data = ''
            if 'title' in item:
                text_data += item['title']
            if 'snippet' in item:
                text_data += item['snippet']
            search_texts.append(text_data)
        
        return [], search_texts

    elif search_type == 'img_search_img':
        image_search_path = os.path.join(save_path, dataset_name, 'image_search_res_{}.json'.format(idx))
        if os.path.exists(image_search_path):
            print("Image Done!!!")
            with open(image_search_path, 'r') as f_tmp:
                search_result = json.load(f_tmp)
                search_images, search_texts = parse_image_search_result_by_image(search_result, save_path, idx, conversation_num)
                if len(search_texts) == 0:
                    print('Extra image search!')
                    search_result = search_image_by_image_url(query)
                    search_images, search_texts = parse_image_search_result_by_image(search_result, save_path, idx, conversation_num)
                return search_images, search_texts
        else:
            search_result = search_image_by_image_url(query)
            search_images, search_texts = parse_image_search_result_by_image(search_result, save_path, idx, conversation_num)
            return search_images, search_texts

    elif search_type == 'text_search_img':
        search_result = search_image_by_text(query)
        search_images, search_texts = parse_image_search_result_by_text(search_result, save_path, idx, conversation_num)
        return search_images, search_texts


#测试
'''save_path='./dataset/TEST_1'     
#input_url = "https://mitalinlp.oss-cn-hangzhou.aliyuncs.com/rallm/mm_data/vfreshqa_datasets_v2/Freshqa_en_zh/Freshqa_en_extracted_images/image_2.jpeg"
input_url = "https://mitalinlp.oss-cn-hangzhou.aliyuncs.com/rallm/mm_data/vfreshqa_datasets_v2/Freshqa_en_zh/Freshqa_en_extracted_images/image_10.jpeg"
#input_url = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://en.wikipedia.org/wiki/Sports_car&ved+2ahUKEwid2sTupb6JAxXamYQIHeetEfoQFnoECAsQAQ"
#input_url = "http://t1.gstatic.com/licensed-image?q=tbn:ANd9GcRPM1uC4w4aIgO5b1jmYmcdLdq8GHFTI3J8Z2XeYMBQKmTJn3_obFn5Q9YAVMzHx764"
#input_url = "https://www.pcarmarket.com/static/media/uploads/galleries/photos/uploads/galleries/22387-pasewark-1986-porsche-944/.thumbnails/IMG_7102.JPG.jpg/IMG_7102.JPG-tiny-2048x0-0.5x0.jpg"
results =   search_image_by_image_url(input_url)
search_images, search_texts=parse_image_search_result_by_image(results, save_path, 0, 0)
print(search_images)
print(search_texts)
#print(results)'''

#测试
'''text="Have humans landed on Mars? Year of landing on Mars by humans"
results=search_text_by_text(text)
search_texts = []
        
for item in results:
    text_data = ''
    if 'title' in item:
        text_data += item['title']
    if 'snippet' in item:
        text_data += item['snippet']
    search_texts.append(text_data)

print(search_texts)
    '''
