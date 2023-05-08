# -*- coding: utf-8 -*-
"""
@Author  : Xhunmon 
@Time    : 2023/4/22 21:54
@FileName: utlis.py
@desc: 
"""
import base64
import configparser
import datetime
import io
import locale
import os
import shutil

import time
from PIL import Image
import numpy as np
import PySimpleGUI as sg


class Key:
    """
    统一管理本地字符串
    """
    PROXY_ENABLE = 'proxy_enable'  # settings
    TYPE_INPUT = 'type_input'  # settings
    TYPE_CHAT = 'Text Chat'  # settings
    TYPE_CREATE = 'Image Create'  # settings
    TYPE_EDIT = 'Image Edit'  # settings
    PROXY_LAYOUT = 'proxy_layout'  # settings
    PROXY_INPUT = 'proxy_input'  # settings
    API_KEY = 'api_key'  # settings
    FOLDER_INPUT = 'folder_input'  # settings
    SAVE_OUT_ENABLE = 'save_out_enable'  # settings
    SAVE_OUT_LAYOUT = 'save_out_layout'  # settings
    SAVE_ONE_FILE = 'save_one_file'  # settings
    FOLDER_CLICK = 'folder_click'  # settings
    MODEL_INPUT = 'model_input'  # settings
    LANGUAGE_INPUT = 'language_select'  # settings
    LANGUAGE_EN = 'English'  # settings
    LANGUAGE_ZH = '中文'  # settings
    LANGUAGE_DEFAULT = 'English'  # settings
    MODEL_DEFAULT = 'gpt-3.5-turbo'  # settings
    THEME = 'theme'  # settings
    STREAM_ENABLE = 'stream_enable'  # settings
    RESTART_WINDOW = 'restart_window'  # settings
    FULL_TRANSLATE = 'full_translate'  # settings
    LANGUAGE = 'language'  # config

    # main
    M_PRE = 'Pre'
    M_NEXT = 'Next'
    M_SAVE = 'Save'
    M_SAVE_ALL = 'SaveALL'
    M_CLEAR = 'Clear'
    M_RUN = 'Run'
    M_COPY = 'Copy'
    M_FILE = 'File'
    M_SETTINGS = 'Settings'
    M_EXIT = 'Exit'


def get_cache(key: str, default=None):
    """
    获取本地的数据
    :param key:
    :param default:
    :return:
    """
    return sg.user_settings_get_entry(key, default)


def save_cache(key: str, value):
    """
    将数据保存到本地
    :param key:
    :param value:
    :return:
    """
    sg.user_settings_set_entry(key, value)


def build_file_name(src, new_name):
    """
    根据文件路径，生成在文件同目录的文件名称，如：/xx/test.jpg --> /xx/new_name
    """
    folder = os.path.dirname(src)
    filename, ext = os.path.splitext(src)
    return os.path.join(folder, '{}'.format(new_name))


def get_str_date():
    # 获取当前时间戳
    current_timestamp = int(time.time())
    # 将时间戳转换成datetime对象
    current_datetime = datetime.datetime.fromtimestamp(current_timestamp)
    # 将datetime对象格式化成字符串
    current_time_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    return current_time_str


def save_image_by_base64(base64_string, file_path):
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_string))
        f.close()


def crop_resize_2_png(src, max_size=1024):
    """
    最终是正方形，1.最小的边 > max_size时，先缩放；2。再判断是否是矩形，不是就进行裁剪；3.是否需要旋转回正
    """
    dst = build_file_name(src, 'ai_source.png')
    im = Image.open(src)  # 读入文件
    im = im.convert('RGBA')  # 修改颜色通道为RGBA
    width = im.size[0]
    height = im.size[1]
    min_size = min(width, height)
    # 缩放 w1/h1 = w2/h2 --> 最小的为准
    if min_size > max_size:
        if width < height:
            height = int(max_size * height / width)
            width = max_size
        else:
            width = int(width * max_size / height)
            height = max_size
        im = im.resize((width, height))
        min_size = min(width, height)
    # 因为需要矩形，以最小的边为准，进行裁剪
    if width != height:
        # 计算左上角的坐标（使图像居中）
        x = (width - min_size) // 2
        y = (height - min_size) // 2
        im = im.crop((x, y, x + min_size, y + min_size))
    # 旋转回正
    try:
        exif = im.getexif()
        if exif:
            orientation = exif.get(274)
            if orientation == 3:
                im = im.rotate(180, expand=True)
            elif orientation == 6:
                im = im.rotate(270, expand=True)
            elif orientation == 8:
                im = im.rotate(90, expand=True)
    except:
        pass
    im.save(dst)
    # 获取二进制值进行操作
    bio = io.BytesIO()
    im.save(bio, format="PNG")
    # bio.getvalue()
    return dst, bio


def build_mask(src, draw):
    """ 两个必须正方形
    生成openai所需要的mask图片，耗时操作需要在子线程操作。把draw全部像素遍历一遍，找出不是白色值的坐标，然后在src上把该坐标设置为完全透明
    如果 src为crop_resize_2_png后的原图，draw绘制时可能比src小。因此需要判断缩放到src尺寸，再进行操作。
    """
    dst = build_file_name(src, 'ai_mask.png')
    im_src = Image.open(src)
    size_src = im_src.size[0]
    im_draw = Image.open(draw)
    size_draw = im_draw.size[0]
    if size_src != size_draw:
        im_draw = im_draw.resize((size_src, size_src))

    im_new = Image.new('RGBA', (size_src, size_src))
    for w in range(size_src):
        for h in range(size_src):
            color_draw = im_draw.getpixel((w, h))
            color_src = im_src.getpixel((w, h))
            if color_draw[0] == 255 and color_draw[1] == 255 and color_draw[2] == 255:
                color_new = color_src
            else:
                color_new = (color_src[0], color_src[1], color_src[2], 0)
            im_new.putpixel((w, h), color_new)

    im_new.save(dst)  # 保存
    return dst


def is_support_img(path: str):
    # bmp，jpg，png，tif，gif，pcx，tga，exif，fpx，svg，psd，cdr，pcd，dxf，ufo，eps，ai，raw，WMF，webp，avif，apng
    filename, ext = os.path.splitext(path)
    if ext in ['.jpg', '.png', '.svg', '.webp']:
        return True
    return False


def read(file_path) -> str:
    '''读取txt文本内容'''
    content = None
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            f.close()
    except Exception as e:
        print(e)
    return content


def get_theme():
    """
    Get the theme to use for the program
    Value is in this program's user settings. If none set, then use PySimpleGUI's global default theme
    :return: The theme
    :rtype: str
    """
    theme = get_cache(Key.THEME, '')
    if theme == '':
        theme = sg.OFFICIAL_PYSIMPLEGUI_THEME  # 默认主题
    return theme


language, encoding = locale.getdefaultlocale()


def is_zh_language():
    cache = get_cache(Key.LANGUAGE_INPUT, None)
    if cache:
        return cache != Key.LANGUAGE_EN
    if language and 'zh' in language:
        save_cache(Key.LANGUAGE_INPUT, Key.LANGUAGE_ZH)
        return True
    save_cache(Key.LANGUAGE_INPUT, Key.LANGUAGE_EN)
    return False


class Config(object):
    # baseDir = os.path.dirname(os.path.realpath(sys.argv[0]))
    md_sep = '\n\n' + '-' * 10 + '\n'
    encodings = ["utf8", "gbk"]

    api_key = ""
    api_base = ""
    model = "gpt-3.5-turbo"
    prompt = []
    stream = True
    response = False
    proxy = ""
    save_out = False
    folder = ""
    repeat = True
    is_loading = False


class IniConfig(object):
    def __init__(self):
        self.reset()

    def reset(self):
        asset_path = os.path.join(os.path.dirname(__file__), 'asset')
        config_path = os.path.join(asset_path, 'config.ini')
        ch_ini = os.path.join(asset_path, 'ch.ini')
        en_ini = os.path.join(asset_path, 'en.ini')
        ini = ch_ini if is_zh_language() else en_ini
        self.language = configparser.ConfigParser()
        self.language.read(ini, encoding='utf-8')
        self.cfg = configparser.ConfigParser()
        self.cfg.read(config_path, encoding='utf-8')

    def full(self, tag, name):
        return self.language[tag][name]

    def main(self, name):
        return self.full('Main', name)

    def settings(self, name):
        return self.full('Settings', name)

    def loading(self, name):
        return self.full('Loading', name)

    def language(self, name):
        return self.full('Language', name)

    def config(self, name):
        return self.cfg['Config'][name]


conf = IniConfig()
