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
import locale
import os
import time

import PySimpleGUI as sg


class Key:
    """
    统一管理本地字符串
    """
    PROXY_ENABLE = 'proxy_enable'  # settings
    TYPE_INPUT = 'type_input'  # settings
    TYPE_DEFAULT = 'Text Chat'  # settings
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