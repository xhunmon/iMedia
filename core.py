# -*- coding: utf-8 -*-
"""
@Author  : Xhunmon 
@Time    : 2023/4/25 15:37
@FileName: core.py
@desc: 
"""
import threading
from datetime import datetime

import openai
import requests

from utils import *


class Gpt(object):
    callback_status = None

    def __init__(self, config: Config):
        self.session = []
        self.api_prompt = []
        self.cfg = config
        self.update_config(config)
        self.content = ""
        self.size = ""
        self.num = ""
        self.edit_file = ''
        self.mask_file = ''
        self.is_change = False
        self.is_finish = True
        gpt_t = threading.Thread(target=self.start)
        gpt_t.setDaemon(True)
        gpt_t.start()

    def update_config(self, config: Config):
        self.cfg = config
        openai.api_key = self.cfg.api_key
        if self.cfg.api_base:
            openai.api_base = self.cfg.api_base
        openai.proxy = self.cfg.proxy if self.cfg.proxy else None
        self.content = ''
        self.is_change = False
        self.is_finish = True

    def start(self):
        while True:
            if self.is_finish:
                while not self.is_change:
                    time.sleep(0.3)
                self.is_change = False
                self.is_finish = False
                self.handle_input(self.content)
            time.sleep(1)

    def content_change(self, content: str, size=None, num=1, edit_file='', mask_file=''):
        if not content:
            return
        self.content = content
        self.size = size
        self.num = num
        self.edit_file = edit_file
        self.mask_file = mask_file
        self.is_change = True

    def handle_input(self, content: str):
        """impl by son"""
        pass


class GptImgCreate(Gpt):
    def __init__(self, config: Config):
        super().__init__(config)

    def handle_input(self, content: str):
        """impl by son"""
        if not content:
            return
        self.is_finish = False
        try:
            Gpt.callback_status(state=1)
            response = openai.Image.create(
                prompt=content,
                # response_format="b64_json",
                n=int(self.num),
                size=self.size
            )
            urls = []
            for choice in response['data']:
                urls.append(choice['url'].strip())
            images = []
            for url in urls:
                image_response = requests.get(url)
                # image = Image.open(BytesIO(image_response.content))
                # images[0].show()
                image = base64.b64encode(image_response.content).decode('utf-8')
                images.append(image)
            Gpt.callback_status(images, state=4)
        except Exception as e:
            Gpt.callback_status("Exception:{}".format(e), state=5)
        Gpt.callback_status(state=3)
        self.is_finish = True


class GptImgEdit(Gpt):
    def __init__(self, config: Config):
        super().__init__(config)

    def handle_input(self, content: str):
        """impl by son"""
        if not content:
            return
        self.is_finish = False
        try:
            Gpt.callback_status(state=1)
            response = openai.Image.create_edit(
                image=open(self.edit_file, "rb"),
                mask=open(self.mask_file, 'rb'),
                prompt=content,
                # response_format="b64_json",
                n=int(self.num),
                size=self.size
            )
            urls = []
            for choice in response['data']:
                urls.append(choice['url'].strip())
            images = []
            for url in urls:
                image_response = requests.get(url)
                # image = Image.open(BytesIO(image_response.content))
                # images[0].show()
                image = base64.b64encode(image_response.content).decode('utf-8')
                images.append(image)
            Gpt.callback_status(images, state=4)
        except Exception as e:
            Gpt.callback_status("Exception:{}".format(e), state=5)
        Gpt.callback_status(state=3)
        self.is_finish = True


class GptTxt(Gpt):

    def __init__(self, config: Config):
        super().__init__(config)

    def query_openai_stream(self, data) -> str:
        messages = []
        messages.extend(self.api_prompt)
        messages.extend(data)
        answer = ""
        try:
            Gpt.callback_status(state=1)
            response = openai.ChatCompletion.create(
                model=self.cfg.model,
                messages=messages,
                stream=True)
            for part in response:
                finish_reason = part["choices"][0]["finish_reason"]
                if "content" in part["choices"][0]["delta"]:
                    content = part["choices"][0]["delta"]["content"]
                    answer += content
                    Gpt.callback_status(content, state=2)
                elif finish_reason:
                    pass
            Gpt.callback_status("\n\n", state=2)
        except KeyboardInterrupt:
            Gpt.callback_status("Canceled", state=2)
        except openai.error.OpenAIError as e:
            Gpt.callback_status("OpenAIError:{}".format(e), state=2)
            answer = ""
        except Exception as e:
            Gpt.callback_status("Error:{}".format(e), state=2)
            answer = ""
        return answer

    def handle_input(self, content: str):
        if not content:
            return
        self.is_finish = False
        self.session.append({"role": "user", "content": content})
        if self.cfg.stream:
            answer = self.query_openai_stream(self.session)
        else:
            answer = self.query_openai(self.session)
        if not answer:
            self.session.pop()
        elif self.cfg.response:
            self.session.append({"role": "assistant", "content": answer})
        if answer:
            try:
                if self.cfg.save_out:
                    if self.cfg.folder and not os.path.exists(self.cfg.folder):
                        os.makedirs(self.cfg.folder)
                    wfile = os.path.join(self.cfg.folder, "gpt.md" if self.cfg.repeat else "gpt_{}.md".format(
                        datetime.now().strftime("%Y%m%d%H%M:%S")))
                    if self.cfg.repeat:
                        with open(wfile, mode='a', encoding="utf-8") as f:
                            f.write("MY:\n{}\n".format(content))
                            f.write("\nGPT:\n{}\n\n".format(answer))
                            f.close()
                    else:
                        with open(wfile, mode='w', encoding="utf-8") as f:
                            f.write("MY:\n{}\n".format(content))
                            f.write("\nGPT:{}".format(answer))
                            f.close()
            except Exception as e:
                Gpt.callback_status("Write error: {} ".format(e), state=2)
        Gpt.callback_status(state=3)
        self.is_finish = True

    def query_openai(self, data) -> str:
        messages = []
        messages.extend(self.api_prompt)
        messages.extend(data)
        content = ''
        try:
            Gpt.callback_status(state=1)
            response = openai.ChatCompletion.create(
                model=self.cfg.model,
                messages=messages
            )
            content = response["choices"][0]["message"]["content"]
            Gpt.callback_status(content, state=2)
        except openai.error.OpenAIError as e:
            Gpt.callback_status("OpenAI error: {} ".format(e), state=2)
        except Exception as e:
            Gpt.callback_status("Error:{}".format(e), state=2)
        Gpt.callback_status(state=3)
        return content
