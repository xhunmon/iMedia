[English](README.md) | 简体中文

根据OpenAI官方API实现一个简单实用的智能媒体界面工具，有ChatGPT 3.5/4聊天，生成图片等，可保存输出的记录，帮助你工作和娱乐，Win、Mac平台开箱即用。

```HTML
<video src="doc/look.mp4" controls="controls" width="849" height="592"></video>
```


# 安装
- 1.注册[OpenAI](https://openai.com/) 账号
- 2.生成[API_KEY](https://platform.openai.com/account/api-keys), 目前ChatGPT 4.0需要付费
- 2.克隆项目
```
git clone https://github.com/xhunmon/iMedia.git
```
- 3.进入目录
```shell
cd iMedia
```
- 4.进行安装
```shell
pip3 install -r requirements.txt
```
- 5.运行
```shell
python3 main.py
```

- 6.打包成`mac.app`或`win.exe`（可选）
```shell script
pyinstaller --windowed --name ChatGPT --add-data "asset/config.ini:asset" --add-data  "asset/ch.ini:asset" --add-data "asset/en.ini:asset"  --icon asset/logo.png main.py core.py utils.py ui.py
```


# 计划
- [x] 已支持: gpt-3.5-turbo/gpt-4/gpt-4-32k
- [x] 已支持把聊天记录自动保存到文件
- [x] 支持代理: HTTP/HTTPS/SOCKS4A/SOCKS5
- [x] 打包成 MacOS App
- [ ] 打包成 Window exe
- [x] 根据提示生成图片
- [ ] 编辑图片
- [ ] 生成图片的变体
- [ ] 音频变成文本

# 链接
- API key generated: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
- [https://platform.openai.com/docs/api-reference/images/create](https://platform.openai.com/docs/api-reference/images/create)
