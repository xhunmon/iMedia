# -*- coding: utf-8 -*-
"""
@Author  : Xhunmon 
@Time    : 2023/4/21 23:03
@FileName: main.py
@desc: 
"""

import io
import os
import shutil

import PySimpleGUI as sg
from PIL import Image, ImageColor, ImageDraw, ImageGrab

from core import *
from ui import *

colors = list(ImageColor.colormap.keys())

CANVAS_LENGTH = 400


class MainWin(object):
    def __init__(self):
        self.cfg = Config()
        self.g_window = None
        self.gpt = None
        self.update_config()
        self.is_loading = False
        self.imgs = []
        self.img_index = 0
        self.edit_file = ''
        self.fun_type = get_cache(Key.TYPE_INPUT, Key.TYPE_CHAT)
        self.img_draw_id = None
        self.img_source_path = None
        self.img_mask_path = None
        self.img_draw_path = '/Users/Qincji/Downloads/ai_draw_temp.png'
        laod_t = threading.Thread(target=self.show_loading)
        laod_t.setDaemon(True)
        laod_t.start()

    def update_init(self):
        self.update_config()
        self.is_loading = False
        self.imgs = []
        self.img_index = 0
        self.fun_type = get_cache(Key.TYPE_INPUT, Key.TYPE_CHAT)

    def make_window(self):
        """
        Creates the main window
        :return: The main window object
        :rtype: (sg.Window)
        """
        self.update_init()
        sg.theme(get_theme())
        top_layout = [sg.Text(conf.main('Description'), font='Any 15', size=(60, 1), justification='left'),
                      sg.Column([[sg.B(conf.main(Key.M_SETTINGS))]], justification='right')]
        txt_in = [[sg.Multiline(size=(80, 2), autoscroll=True, font=("Andale Mono", 16), write_only=True, expand_x=True,
                                key='IN_TEXT')]]
        in_layout = sg.Col([
            [sg.TabGroup([[sg.Tab('Input', txt_in)]], k='_INGROUP_')], [sg.Text(size=(12, 1), key='-OUT-')],
        ])
        img_btns = [
            sg.Combo(['256x256', '512x512', '1024x1024'], default_value='512x512', readonly=True, key='_IMAGE_SIZE_'),
            sg.Combo(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], default_value='1', readonly=True,
                     key='_IMAGE_COUNT_'),
            sg.B(conf.main(Key.M_PRE)), sg.B(conf.main(Key.M_NEXT)), sg.B(conf.main(Key.M_SAVE)),
            sg.B(conf.main(Key.M_SAVE_ALL)),
        ]
        img_edit_btn = [
            sg.Text("Fill"),
            sg.Combo(colors, default_value=colors[0], key="_FILL_COLOR_", enable_events=True, readonly=True),
            sg.Text("Outline"),
            sg.Combo(colors, default_value=colors[0], key="_OUTLINE_COLOR_", enable_events=True, readonly=True),
            sg.Text("Width"),
            sg.Input("3", size=(5, 1), key="_WIDTH_", enable_events=True),
            sg.Text("", pad=(50, 1)),
            sg.Input('', key="_IMG_IN_", enable_events=True, visible=False),
            sg.FileBrowse(conf.main('EditImg'), file_types=(('ALL files', '.*')), target='_IMG_IN_'),
        ]
        btn_layout = sg.Col([
            [sg.Image(data=conf.config('Loading').encode('utf-8'), key='_IMG_LOAD_'),
             sg.Column([[sg.B(conf.main(Key.M_RUN)), sg.B(conf.main(Key.M_CLEAR)), sg.B(conf.main(Key.M_COPY))]]),
             sg.Column([img_btns], pad=(50, 1), k='_IMG_LAYOUT_', expand_x=True, expand_y=False,
                       visible=self.fun_type != Key.TYPE_CHAT), ],
            [sg.Column([img_edit_btn], pad=(1, 1), k='_IMG_EDIT_LAYOUT_', expand_x=True, expand_y=False,
                       visible=self.fun_type == Key.TYPE_EDIT)]
        ], expand_x=True, expand_y=False)

        img_big = [[sg.Image(key='_IMG_BIG_')]]
        txt_out = [[sg.Multiline(size=(80, 30), font='Courier 12', k='_TXT_OUT_', reroute_stdout=True,
                                 echo_stdout_stderr=True, reroute_cprint=True)]]
        img_draw = [[sg.Graph(canvas_size=(CANVAS_LENGTH, CANVAS_LENGTH), graph_bottom_left=(CANVAS_LENGTH, 0),
                              graph_top_right=(0, CANVAS_LENGTH), key="-GRAPH-", enable_events=True,
                              background_color='white', drag_submits=True)]]
        bottom_layout = sg.pin(sg.Column([
            [sg.T(conf.main('Business'), font='Default 12', pad=(0, 0)),
             sg.T(conf.main('Email') + conf.config('Email') + '  ', font='Default 12', pad=(0, 0)),
             sg.T(conf.main('WeChat') + conf.config('Wechat') + '  ', font='Default 12', pad=(0, 0)),
             sg.T(conf.main('Version') + conf.config('Version'))]
        ], pad=(0, 0), k='-OPTIONS BOTTOM-', expand_x=True, expand_y=False), expand_x=True, expand_y=False)

        out_layout = sg.Col([
            [sg.TabGroup(
                [[sg.Tab('Output Text', txt_out, key='_TAB_TEXT_'),
                  sg.Tab('Output Image', img_big, key='_TAB_IMAGE_'),
                  sg.Tab('Draw Image', img_draw, key='_TAB_DRAW_')]],
                k='_OUT_GROUP_')],
            [sg.Text(size=(12, 1), key='-OUT-')],
        ])
        # ----- Full layout ----- sg.Button(conf.main(Key.M_EXIT))
        layout = [
            [top_layout],
            [sg.Pane([in_layout, btn_layout, out_layout], handle_size=5, orientation='v',
                     border_width=0,
                     relief=sg.RELIEF_GROOVE, expand_x=True, expand_y=True, k='_PANE_')],
            [bottom_layout, sg.Sizegrip()]]
        # --------------------------------- Create Window ---------------------------------
        window = sg.Window(conf.main('Title'), layout, finalize=True, resizable=True, use_default_focus=False)
        self.g_window = window
        # window.set_min_size(window.size)
        self.show_tab()
        window['_INGROUP_'].expand(True, True, True)
        window['_OUT_GROUP_'].expand(True, True, True)
        window['IN_TEXT'].expand(True, True, True)
        window['_IMG_BIG_'].expand(True, True, True)
        window['_TXT_OUT_'].expand(True, True, True)
        window['_PANE_'].expand(True, True, True)
        window.bind('<F1>', 'Exit')
        # window.bind("<Enter>", 'Enter')
        window['IN_TEXT'].bind('<Return>', ' Return')
        window.bring_to_front()
        return window

    def show_loading(self):
        while True:
            if self.g_window and self.is_loading:
                self.g_window.Element('_IMG_LOAD_').UpdateAnimation(conf.config('Loading').encode('utf-8'),
                                                                    time_between_frames=50)
            else:
                time.sleep(0.3)

    def show_tab(self):
        if self.fun_type == Key.TYPE_CREATE:
            self.g_window['_TAB_IMAGE_'].select()
        elif self.fun_type == Key.TYPE_EDIT:
            self.g_window['_TAB_DRAW_'].select()
        else:
            self.g_window['_TAB_TEXT_'].select()

    def create_gpt(self):
        if self.fun_type == Key.TYPE_CREATE:
            self.gpt = GptImgCreate(self.cfg)
        elif self.fun_type == Key.TYPE_EDIT:
            self.gpt = GptImgEdit(self.cfg)
        else:
            self.gpt = GptTxt(self.cfg)

    def update_layout_by_setting(self):
        is_img_now = get_cache(Key.TYPE_INPUT, Key.TYPE_CHAT)
        if is_img_now != self.fun_type:  # 更改了模式
            self.fun_type = is_img_now
            self.create_gpt()
        if self.g_window:
            self.g_window['_IMG_LAYOUT_'].update(visible=self.fun_type != Key.TYPE_CHAT)
            self.show_tab()

    def update_config(self):
        self.cfg.api_key = get_cache(Key.API_KEY, '')
        self.cfg.model = get_cache(Key.MODEL_INPUT, Key.MODEL_DEFAULT)
        self.cfg.stream = get_cache(Key.STREAM_ENABLE, True)
        self.cfg.proxy = get_cache(Key.PROXY_INPUT, '') if get_cache(Key.PROXY_ENABLE, False) else ''
        if get_cache(Key.SAVE_OUT_ENABLE, False):
            self.cfg.save_out = True
            self.cfg.folder = get_cache(Key.FOLDER_INPUT, '')
            self.cfg.repeat = get_cache(Key.SAVE_ONE_FILE, True)
        else:
            self.cfg.save_out = False
        if self.gpt:
            self.gpt.update_config(self.cfg)

    def callback_status(self, content: str = None, state: int = 1):
        """
        @state: 1 prepare( show loading); 2 request...(loading, get data);
                3 finish(done or fail); 4 image=[], 5 image error
        """
        if not self.g_window:
            return
        if state == 1:
            self.is_loading = True
            cur = self.g_window['_TXT_OUT_'].get()
            if len(cur) > 0:
                self.g_window['_TXT_OUT_'].update("\n{}\n".format('-' * 150), append=True)
                self.g_window['_TXT_OUT_'].set_vscroll_position(1.0)
        elif state == 2:
            self.g_window['_TXT_OUT_'].update(content, append=True)
            self.g_window['_TXT_OUT_'].set_vscroll_position(1.0)
        elif state == 3:
            self.is_loading = False
        elif state == 4:  # Image
            self.imgs = content
            self.img_index = 0
            if len(self.imgs) > 0:
                # self.imgs[0].show()
                self.g_window.Element('_IMG_BIG_').update(data=self.imgs[0], )
        elif state == 5:  # Image
            self.g_window['IN_TEXT'].update(content, append=True)

    def save_element_as_file(self, element, window):
        widget = element.Widget
        box = (widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_rootx() + widget.winfo_width(),
               widget.winfo_rooty() + widget.winfo_height())
        grab = ImageGrab.grab(bbox=box)
        grab.save(self.img_draw_path)
        element.erase()
        # 等待结果
        self.g_window['_TAB_IMAGE_'].select()
        self.img_mask_path = build_mask(self.img_source_path, self.img_draw_path)
        self.gpt.content_change(window['IN_TEXT'].get(), window['_IMAGE_SIZE_'].get(),
                                window['_IMAGE_COUNT_'].get(), self.img_source_path, self.img_mask_path)

    def show(self):
        # icon = sg.EMOJI_BASE64_HAPPY_WINK
        icon = conf.config('Logo').encode('utf-8')
        # icon = os.path.join(os.path.dirname(__file__), 'doc', 'doc/logo.png')
        # sg.user_settings_filename('psgdemos.json')
        sg.set_options(icon=icon)
        window = self.make_window()
        self.g_window = window
        window.force_focus()
        counter = 0
        graph = window["-GRAPH-"]  # type: sg.Graph
        Gpt.callback_status = self.callback_status
        dragging = False
        start_point = end_point = None

        while True:
            event, values = window.read()
            # print(event, values)

            counter += 1
            if event in (sg.WINDOW_CLOSED, conf.main(Key.M_EXIT)):
                break
            elif event == conf.main(Key.M_SETTINGS):
                change, restart = settings_show()
                if change:  # settings 可能更改的内容：主题，代理，高级
                    type_now = get_cache(Key.TYPE_INPUT, Key.TYPE_CHAT)
                    if restart or type_now != self.fun_type:  # 更改了模式
                        self.update_layout_by_setting()
                        conf.reset()
                        window.close()
                        window = self.make_window()
                        self.g_window = window
                    else:
                        self.update_config()
                        self.update_layout_by_setting()

            elif event == conf.main(Key.M_RUN) or event == 'IN_TEXT Return':  # IN_TEXT 的回车键监听, 需要从input获取到数据，然后进行翻译
                search = window['IN_TEXT'].get()
                if not self.gpt:
                    self.create_gpt()
                else:
                    self.gpt.update_config(self.cfg)
                if self.fun_type == Key.TYPE_EDIT:
                    graph.delete_figure(self.img_draw_id)
                    t = threading.Thread(target=self.save_element_as_file, args=(graph, window))
                    t.start()

                else:
                    self.gpt.content_change(search, window['_IMAGE_SIZE_'].get(),
                                            window['_IMAGE_COUNT_'].get(), self.edit_file)
                window['IN_TEXT'].update(search)  # Remove spaces
            elif event == conf.main(Key.M_CLEAR):
                window['IN_TEXT'].update('')
                window['_TXT_OUT_'].update('')
            elif event == conf.main(Key.M_COPY):
                sg.clipboard_set(window['_TXT_OUT_'].get())
            elif event == conf.main(Key.M_PRE):
                index = self.img_index - 1
                if 0 <= index <= len(self.imgs) - 1:
                    window['_IMG_BIG_'].update(data=self.imgs[index], )
                    self.img_index = index
            elif event == conf.main(Key.M_NEXT):
                index = self.img_index + 1
                if 0 <= index <= len(self.imgs) - 1:
                    window['_IMG_BIG_'].update(data=self.imgs[index], )
                    self.img_index = index
            elif event == conf.main(Key.M_SAVE):
                index = self.img_index
                if 0 <= index <= len(self.imgs) - 1:
                    save_image_by_base64(self.imgs[index],
                                         os.path.join(self.cfg.folder, '{}-{}.png'.format(get_str_date(), index)))
            elif event == conf.main(Key.M_SAVE_ALL):
                for index in range(0, len(self.imgs)):
                    save_image_by_base64(self.imgs[index],
                                         os.path.join(self.cfg.folder, '{}-{}.png'.format(get_str_date(), index)))
            if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
                x, y = values["-GRAPH-"]
                if not dragging:
                    start_point = (x, y)
                    dragging = True
                else:
                    end_point = (x, y)
                if None not in (start_point, end_point):
                    graph.draw_point((x, y), size=20)
            elif event == '_IMG_IN_':
                file_path: str = values['_IMG_IN_']
                if is_support_img(file_path):
                    self.img_source_path, bio = crop_resize_2_png(file_path, CANVAS_LENGTH)
                    self.img_draw_id = graph.draw_image(data=bio.getvalue(), location=(CANVAS_LENGTH, CANVAS_LENGTH))
                else:
                    pass
            elif event == 'Version':
                sg.popup_scrolled(sg.get_versions(), keep_on_top=True, non_blocking=True)
        window.close()


if __name__ == '__main__':
    MainWin().show()
