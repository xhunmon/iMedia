# -*- coding: utf-8 -*-
"""
@Author  : Xhunmon 
@Time    : 2023/4/21 23:03
@FileName: main.py
@desc: 
"""
import PySimpleGUI as sg

from core import *
from ui import settings_show


class MainWin(object):
    def __init__(self):
        self.cfg = Config()
        self.g_window = None
        self.gpt = None
        self.update_config()
        self.is_loading = False
        self.imgs = []
        self.img_index = 0
        self.is_img = get_cache(Key.TYPE_INPUT, Key.TYPE_DEFAULT) != Key.TYPE_DEFAULT
        laod_t = threading.Thread(target=self.show_loading)
        laod_t.setDaemon(True)
        laod_t.start()

    def update_init(self):
        self.update_config()
        self.is_loading = False
        self.imgs = []
        self.img_index = 0
        self.is_img = get_cache(Key.TYPE_INPUT, Key.TYPE_DEFAULT) != Key.TYPE_DEFAULT

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
        btn_layout = sg.Col([
            [sg.Image(data=conf.config('Loading').encode('utf-8'), key='_IMAGE_'),
             sg.Column([[sg.B(conf.main(Key.M_RUN)), sg.B(conf.main(Key.M_CLEAR)), sg.B(conf.main(Key.M_COPY))]]),
             sg.Column([img_btns], pad=(50, 1), k='_IMG_LAYOUT_', expand_x=True, expand_y=False, visible=self.is_img)]
        ], expand_x=True, expand_y=False)
        img_out = [[sg.Image(key='OUT_IMAGE')]]
        txt_out = [[sg.Multiline(size=(80, 30), font='Courier 12', k='OUT_TEXT', reroute_stdout=True,
                                 echo_stdout_stderr=True, reroute_cprint=True)]]
        bottom_layout = sg.pin(sg.Column([
            [sg.T(conf.main('Business'), font='Default 12', pad=(0, 0)),
             sg.T(conf.main('Email') + conf.config('Email') + '  ', font='Default 12', pad=(0, 0)),
             sg.T(conf.main('WeChat') + conf.config('Wechat') + '  ', font='Default 12', pad=(0, 0)),
             sg.T(conf.main('Version') + conf.config('Version'))]
        ], pad=(0, 0), k='-OPTIONS BOTTOM-', expand_x=True, expand_y=False), expand_x=True, expand_y=False)

        out_layout = sg.Col([
            [sg.TabGroup(
                [[sg.Tab('Output Text', txt_out, key='_TABTEXT_'), sg.Tab('Output Image', img_out, key='_TABIMAGE_')]],
                k='_OUTGROUP_')],
            [sg.Text(size=(12, 1), key='-OUT-')],
        ])
        # ----- Full layout ----- sg.Button(conf.main(Key.M_EXIT))
        layout = [
            [top_layout],
            [sg.Pane([in_layout, btn_layout, out_layout], handle_size=5, orientation='v', border_width=0,
                     relief=sg.RELIEF_GROOVE, expand_x=True, expand_y=True, k='_PANE_')],
            [bottom_layout, sg.Sizegrip()]]
        # --------------------------------- Create Window ---------------------------------
        window = sg.Window(conf.main('Title'), layout, finalize=True, resizable=True, use_default_focus=False)
        self.g_window = window
        # window.set_min_size(window.size)
        self.g_window['_TABIMAGE_' if self.is_img else '_TABTEXT_'].select()
        window['_INGROUP_'].expand(True, True, True)
        window['_OUTGROUP_'].expand(True, True, True)
        window['IN_TEXT'].expand(True, True, True)
        window['OUT_IMAGE'].expand(True, True, True)
        window['OUT_TEXT'].expand(True, True, True)
        window['_PANE_'].expand(True, True, True)
        window.bind('<F1>', 'Exit')
        # window.bind("<Enter>", 'Enter')
        window['IN_TEXT'].bind('<Return>', ' Return')
        window.bring_to_front()
        return window

    def show_loading(self):
        while True:
            if self.g_window and self.is_loading:
                self.g_window.Element('_IMAGE_').UpdateAnimation(conf.config('Loading').encode('utf-8'),
                                                                 time_between_frames=50)
            else:
                time.sleep(0.3)

    def update_layout_by_setting(self):
        is_img_now = get_cache(Key.TYPE_INPUT, Key.TYPE_DEFAULT) != Key.TYPE_DEFAULT
        if is_img_now != self.is_img:  # 更改了模式
            self.is_img = is_img_now
            self.gpt = GptImg(self.cfg) if self.is_img else GptTxt(self.cfg)
        if self.g_window:
            self.g_window['_IMG_LAYOUT_'].update(visible=is_img_now)
            self.g_window['_TABIMAGE_' if is_img_now else '_TABTEXT_'].select()
            # self.g_window['OUT_IMAGE'].update(visible=is_img_now)
            # self.g_window['OUT_TEXT'].update(visible=not is_img_now)

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
            cur = self.g_window['OUT_TEXT'].get()
            if len(cur) > 0:
                self.g_window['OUT_TEXT'].update("\n{}\n".format('-' * 150), append=True)
                self.g_window['OUT_TEXT'].set_vscroll_position(1.0)
        elif state == 2:
            self.g_window['OUT_TEXT'].update(content, append=True)
            self.g_window['OUT_TEXT'].set_vscroll_position(1.0)
        elif state == 3:
            self.is_loading = False
        elif state == 4:  # Image
            self.imgs = content
            self.img_index = 0
            if len(self.imgs) > 0:
                # self.imgs[0].show()
                self.g_window.Element('OUT_IMAGE').update(data=self.imgs[0], )
        elif state == 5:  # Image
            self.g_window['IN_TEXT'].update(content, append=True)

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
        Gpt.callback_status = self.callback_status

        while True:
            event, values = window.read()
            # print(event, values)

            counter += 1
            if event in (sg.WINDOW_CLOSED, conf.main(Key.M_EXIT)):
                break
            elif event == conf.main(Key.M_SETTINGS):
                change, restart = settings_show()
                if change:  # settings 可能更改的内容：主题，代理，高级
                    is_img_now = get_cache(Key.TYPE_INPUT, Key.TYPE_DEFAULT) != Key.TYPE_DEFAULT
                    if restart or is_img_now != self.is_img:  # 更改了模式
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
                    self.gpt = GptImg(self.cfg) if self.is_img else GptTxt(self.cfg)
                else:
                    self.gpt.update_config(self.cfg)
                self.gpt.content_change(search, window['_IMAGE_SIZE_'].get(),
                                        window['_IMAGE_COUNT_'].get())
                window['IN_TEXT'].update(search)  # Remove spaces
            elif event == conf.main(Key.M_CLEAR):
                window['IN_TEXT'].update('')
                window['OUT_TEXT'].update('')
            elif event == conf.main(Key.M_COPY):
                sg.clipboard_set(window['OUT_TEXT'].get())
            elif event == conf.main(Key.M_PRE):
                index = self.img_index - 1
                if 0 <= index <= len(self.imgs) - 1:
                    window['OUT_IMAGE'].update(data=self.imgs[index], )
                    self.img_index = index
            elif event == conf.main(Key.M_NEXT):
                index = self.img_index + 1
                if 0 <= index <= len(self.imgs) - 1:
                    window['OUT_IMAGE'].update(data=self.imgs[index], )
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

            elif event == 'Version':
                sg.popup_scrolled(sg.get_versions(), keep_on_top=True, non_blocking=True)
        window.close()


if __name__ == '__main__':
    MainWin().show()
