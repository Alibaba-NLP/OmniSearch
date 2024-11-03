from search_api import fine_search
import prompt as prompt

class ConversationManager:
    def __init__(self, qa_agent, dataset_name, save_path):
        self.qa_agent = qa_agent
        self.dataset_name = dataset_name
        self.save_path = save_path
        self.conversation_num = 0
        self.total_image_quota = 9

    def manage_conversation(self, input_question, image_url, idx):
        self.conversation_num = 0
        messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt.sys_prompt_1.format(input_question)},
                {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
            ]
        }
    ]
        current_message = messages

        success, idx, message, answer = self.qa_agent.ask_gpt(messages, idx)
        print("first response:", answer)

        while self.conversation_num < 5:
            if "Final Answer" in answer:
               #生成一个字典 tmp_d，代表助手的角色，并将 message 内容添加到其中。将 tmp_d 添加到 current_message 中以保留完整会话记录。
                tmp_d = {"role": "assistant"}
                tmp_d.update(message)
                current_message.append(tmp_d)
                print(answer)
                print("-------")
                print(answer.split("Final Answer: ")[-1])
                #返回最终答案（去掉 Final Answer: 前缀）、当前会话状态
                return answer.split("Final Answer: ")[-1], current_message
            
            if any(phrase in answer for phrase in ["Image Retrieval with Input Image", "Text Retrieval", "Image Retrieval with Text Query"]):
                tmp_d = {"role": "assistant"}
                tmp_d.update(message)
                current_message.append(tmp_d)
                sub_question = answer.split('<Sub-Question>\n')[-1].split('\n')[0]
                search_images, search_text = self.handle_retrieval(answer, image_url, idx)
                
                contents = self.prepare_contents(search_images,messages,sub_question,idx, search_text, image_url)
                current_message.append({"role": "user", "content": contents})

                success, idx, message, answer = self.qa_agent.ask_gpt(current_message, idx)
                print("conversation step:", self.conversation_num, answer)
                if not success:
                    print("Request failed.")
                    break
            print(self.conversation_num)
            self.conversation_num += 1
        print(answer)
        print(self.conversation_num)
        #print(current_message)
        print("OVER!")
        return answer, current_message

    def handle_retrieval(self, answer, image_url, idx):
        if 'Image Retrieval with Input Image' in answer:
            return fine_search(image_url, 'img_search_img', self.save_path, self.dataset_name, idx, self.conversation_num)
        elif 'Text Retrieval' in answer:
            query = self.extract_query(answer, 'Text Retrieval')
            return fine_search(query, 'text_search_text', self.save_path, self.dataset_name, idx, self.conversation_num)
        elif 'Image Retrieval with Text Query' in answer:
            query = self.extract_query(answer, 'Image Retrieval with Text Query')
            return fine_search(query, 'text_search_img', self.save_path, self.dataset_name, idx, self.conversation_num)

    def extract_query(self, answer, retrieval_type):
        return answer.split(retrieval_type)[-1].replace(':', '').replace('"', '').replace('>', '')

    def prepare_contents(self, search_images,messages,sub_question,idx,search_text, image_url):
        if len(search_images) > 0:
            #断言失败的时候显示(search_text)
            #assert len(search_images) == len(search_text), (search_text)
            contents = [{"type": "text", "text": "Contents of retrieved images: "}]
            use_imgs_num = min(5, self.total_image_quota)
            self.total_image_quota -= use_imgs_num
            for img, txt in zip(search_images[:use_imgs_num], search_text[:use_imgs_num]):
                contents.extend([
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img[0],
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Description: "+txt
                    }
                    ])
        else:
            contents = [
            {
                "type": "text",
                "text": "Below are related documents retrieved, which may be helpful for answering questions later on:"
            }
        ]
            for txt in search_text:
                contents.append({
                    "type": "text",
                    "text": txt
                })
            
            contents.append({
                "type": "text",
                "text": "\nInput Image:"
            })
            contents.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "high"
                }
            })
            contents.append({
                "type": "text",
                "text": sub_question + " Answer:"
            })
            sub_messages = [
                {
                    "role": "user",
                    "content": contents
                }
            ]
           
            #contents = ["Below are related documents retrieved, which may be helpful for answering questions later on:"]
            '''for txt in search_text:
                contents.append(txt)
            contents.append("\nInput Image:")
            contents.append('<img>{}</img>'.format(image_url))
            contents.append(sub_question + ' Answer:')
            messages = '\n'.join(contents)'''
            
            '''contents = [
                {"role": "user","type": "text", "text": "Below are related documents retrieved, which may be helpful for answering questions later on:"}
            ]
            for txt in search_text:
                contents.append({"type": "text", "text": txt})
            contents.append({"type": "text", "text": "Input Image:"})
            contents.append({"type": "image_url", "image_url": {"url": image_url, "detail": "high"}})
            contents.append({"type": "text", "text": sub_question + " Answer:"})
            #messages = '\n'.join(contents)
            messages = contents'''
            success=True
            answer=self.qa_agent.ask_gpt(sub_messages,idx)
            contents = [{"type": "text", "text": "Contents of retrieved documents: "}]
            if success:
                contents.extend([{"type": "text", "text": answer}])
            else:
                for txt in search_text:
                    contents.extend([
                        {
                            "type": "text",
                            "text": txt
                        }
                        ])
        return contents

