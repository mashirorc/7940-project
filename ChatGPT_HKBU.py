# import configparser
import requests
import os
class HKBU_ChatGPT():
    def __init__(self):
        self.modelname = (os.environ['GPT_MODEL'])
        self.access_token = (os.environ['GPT_TOKEN'])
        self.url = (os.environ['GPT_URL'])
        self.version = (os.environ['GPT_VERSION'])
    def submit(self,message):
        conversation = [{"role": "user", "content": message}]
        url = (self.url) + \
            "/deployments/" + (self.modelname) + \
            "/chat/completions/?api-version=" + \
        (self.version)
        headers = { 'Content-Type': 'application/json',
        'api-key': (self.access_token) }
        payload = { 'messages': conversation }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response
if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()
    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)
