# -*- coding: utf-8 -*-
"""
@Author  : Xhunmon 
@Time    : 2023/4/22 22:31
@FileName: ui.py
@desc: 
"""
from utils import *


def settings_show():
    """
    Show the settings window.
    This is where the folder paths and program paths are set.
    Returns True if settings were changed

    :return: True if settings were changed
    :rtype: (bool)
    """
    proxy_enable = get_cache(Key.PROXY_ENABLE, False)
    save_out_enable = get_cache(Key.SAVE_OUT_ENABLE, False)
    restart_enable = get_cache(Key.RESTART_WINDOW, False)

    layout = [
        [sg.T('  ', font='_ 16', size=(45, 1))],
        [sg.T(conf.settings('Engine'), font='_ 16'),
         sg.Combo([Key.TYPE_CHAT, Key.TYPE_CREATE, Key.TYPE_EDIT],
                  default_value=get_cache(Key.TYPE_INPUT, Key.TYPE_CHAT), readonly=True, key=Key.TYPE_INPUT)],
        [sg.Input(size=(38, 1), default_text=get_cache(Key.API_KEY, ''), key=Key.API_KEY),
         sg.T('API KEY', font='_ 12')],
        [sg.Combo(['gpt-3.5-turbo', 'gpt-4', 'gpt-4-32k'], default_value=get_cache(Key.MODEL_INPUT, Key.MODEL_DEFAULT),
                  readonly=True, k=Key.MODEL_INPUT),
         sg.T(conf.settings('Model'), font='_ 12')],
        [sg.CB(conf.settings('Stream'), default=get_cache(Key.STREAM_ENABLE, True), k=Key.STREAM_ENABLE, font='_ 12')],
        [sg.T('  ', font='_ 16', size=(45, 1))],
        [sg.T(conf.settings('Advance'), font='_ 16')],
        [sg.CB(conf.settings('ProxyEnable'), default=proxy_enable, enable_events=True, k=Key.PROXY_ENABLE,
               font='_ 12')],
        [sg.Column([[sg.Input(size=(38, 1), default_text=get_cache(Key.PROXY_INPUT, ''), key=Key.PROXY_INPUT),
                     sg.T(conf.settings('ProxyDesc'), font='_ 12')]], visible=proxy_enable, k=Key.PROXY_LAYOUT)],

        [sg.T('  ', font='_ 6', size=(45, 1))],
        [sg.CB(conf.settings('SaveFile'), default=save_out_enable, enable_events=True, k=Key.SAVE_OUT_ENABLE,
               font='_ 12')],
        [sg.Column([[sg.Input(size=(38, 1), default_text=get_cache(Key.FOLDER_INPUT, ''), key=Key.FOLDER_INPUT),
                     sg.FolderBrowse(conf.settings('Folder'), target=Key.FOLDER_INPUT)],
                    [sg.CB(conf.settings('OneFile'), default=get_cache(Key.SAVE_ONE_FILE, True), k=Key.SAVE_ONE_FILE,
                           font='_ 12')], ], visible=save_out_enable, k=Key.SAVE_OUT_LAYOUT)],
        [sg.Combo([Key.LANGUAGE_ZH, Key.LANGUAGE_EN],
                  default_value=get_cache(Key.LANGUAGE_INPUT, Key.LANGUAGE_DEFAULT), k=Key.LANGUAGE_INPUT),
         sg.T(conf.settings('Language'), font='_ 12')],
        [sg.T('  ', font='_ 6', size=(45, 1))],
        [sg.T(conf.settings('Theme'), font='_ 16')],
        [sg.T(conf.settings('ThemeDesc'), font='_ 11'), sg.T(get_theme(), font='_ 13')],
        [sg.Combo([''] + sg.theme_list(), get_cache(Key.THEME, ''), readonly=True, k=Key.THEME),
         sg.CB(conf.settings('Restart'), default=restart_enable, enable_events=True,
               k=Key.RESTART_WINDOW,
               font='_ 12')],
        [sg.B(conf.settings('Ok'), bind_return_key=True), sg.B(conf.settings('Cancel')), sg.B(conf.settings('Reset'))],
    ]

    window = sg.Window(conf.settings('Title'), layout, finalize=True)
    settings_changed = False

    while True:
        event, values = window.read()
        if event in (conf.settings('Cancel'), sg.WIN_CLOSED):
            break
        if event == conf.settings('Ok'):
            save_cache(Key.TYPE_INPUT, window[Key.TYPE_INPUT].get())
            save_cache(Key.PROXY_ENABLE, window[Key.PROXY_ENABLE].get())
            save_cache(Key.PROXY_INPUT, window[Key.PROXY_INPUT].get())
            save_cache(Key.API_KEY, window[Key.API_KEY].get())
            save_cache(Key.MODEL_INPUT, window[Key.MODEL_INPUT].get())
            save_cache(Key.STREAM_ENABLE, window[Key.STREAM_ENABLE].get())
            save_cache(Key.FOLDER_INPUT, window[Key.FOLDER_INPUT].get())
            save_cache(Key.SAVE_OUT_ENABLE, window[Key.SAVE_OUT_ENABLE].get())
            save_cache(Key.SAVE_ONE_FILE, window[Key.SAVE_ONE_FILE].get())
            save_cache(Key.LANGUAGE_INPUT, window[Key.LANGUAGE_INPUT].get())
            save_cache(Key.THEME, window[Key.THEME].get())
            restart_enable = window[Key.RESTART_WINDOW].get()
            save_cache(Key.RESTART_WINDOW, restart_enable)
            settings_changed = True
            break
        elif event == conf.settings('Reset'):  # 恢复所有默认设置
            save_cache(Key.TYPE_INPUT, Key.TYPE_CHAT)
            save_cache(Key.PROXY_ENABLE, False)
            save_cache(Key.PROXY_INPUT, '')
            save_cache(Key.API_KEY, '')
            save_cache(Key.MODEL_INPUT, Key.MODEL_DEFAULT)
            save_cache(Key.LANGUAGE_INPUT, Key.LANGUAGE_DEFAULT)
            save_cache(Key.STREAM_ENABLE, True)
            save_cache(Key.SAVE_OUT_ENABLE, False)
            save_cache(Key.FOLDER_INPUT, '')
            save_cache(Key.SAVE_ONE_FILE, True)
            save_cache(Key.THEME, '')
            save_cache(Key.RESTART_WINDOW, False)
            restart_enable = window[Key.RESTART_WINDOW].get()
            settings_changed = True
            break
        elif event == Key.PROXY_ENABLE:
            proxy_enable = values[Key.PROXY_ENABLE]
            window[Key.PROXY_ENABLE].update(value=proxy_enable)
            window[Key.PROXY_LAYOUT].update(visible=proxy_enable)
        elif event == Key.SAVE_OUT_ENABLE:
            save_out_enable = values[Key.SAVE_OUT_ENABLE]
            window[Key.SAVE_OUT_ENABLE].update(value=save_out_enable)
            window[Key.SAVE_OUT_LAYOUT].update(visible=save_out_enable)

    window.close()
    return settings_changed, restart_enable
