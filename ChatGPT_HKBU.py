import configparser
import requests
import os
class HKBU_ChatGPT:
    def __init__(self, config_path='./config.ini'):
        # Check if config_path is a string, indicating the path to the config file
        if isinstance(config_path, str):
            self.config = configparser.ConfigParser()
            self.config.read(config_path)
        # Check if config_path is already a ConfigParser object
        elif isinstance(config_path, configparser.ConfigParser):
            self.config = config_path
        else:
            raise ValueError("config_path must be a string or ConfigParser object")

    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        url = (self.config['CHATGPT']['BASICURL'] +
               "/deployments/" + self.config['CHATGPT']['MODELNAME'] +
               "/chat/completions/?api-version=" +
               self.config['CHATGPT']['APIVERSION'])
        headers = {
            'Content-Type': 'application/json',
            # 'api-key': self.config['CHATGPT']['ACCESS_TOKEN']
            'api-key': os.environ['ACCESS_TOKEN_CHATGPT']
        }
        payload = {'messages': conversation}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f'Error: {response.status_code}, {response.text}'

if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()
    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)
