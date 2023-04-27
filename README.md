English | [简体中文](README_ZH.md)  

According to the OpenAI API to achieve a simple and practical intelligent media interface tool with ChatGPT 3.5/4 chat, generate images, etc., can save the output records to help you work and play, Win, Mac platform out of the box.

```HTML
<video src="doc/look.mp4" controls="controls" width="849" height="592"></video>
```


# Use
- 1.Register [OpenAI](https://openai.com/) 
- 2.Create [API_KEY](https://platform.openai.com/account/api-keys)
- 2.Clone
```
git clone https://github.com/xhunmon/iMedia.git
```
- 3.Enter Directory
```shell
cd iMedia
```
- 4.Install
```shell
pip3 install -r requirements.txt
```
- 5.Run
```shell
python3 main.py
```

- 6.Pack `mac.app` or `win.exe` (Option)
```shell script
pyinstaller --windowed --name ChatGPT --add-data "asset/config.ini:asset" --add-data  "asset/ch.ini:asset" --add-data "asset/en.ini:asset"  --icon asset/logo.png main.py core.py utils.py ui.py
```

# Feature
- [x] Support model: gpt-3.5-turbo/gpt-4/gpt-4-32k
- [x] Support for exporting chat logs to files
- [x] Support proxy: HTTP/HTTPS/SOCKS4A/SOCKS5
- [x] Build MacOS App
- [ ] Build Window exe
- [x] Creates an image given a prompt
- [ ] Create image edit
- [ ] Creates a variation of a given image
- [ ] Learn how to turn audio into text

# Link
- API key generated: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
- [https://platform.openai.com/docs/api-reference/images/create](https://platform.openai.com/docs/api-reference/images/create)
