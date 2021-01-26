import os
# import css_parser
# from css_parser.css import CSSStyleSheet, CSSStyleRule, CSSStyleDeclaration, SelectorList, Selector, CSSMediaRule
# from css_parser.util import Seq, Item
#
# parser = css_parser.parse.CSSParser()
#
# style: CSSStyleSheet = parser.parseString("""
# TButton {
#   relief: flat;
#   background: #7f7f7f;
#   foreground: white;
# }
# TButton:focus {
#   relief: flat;
#   background: #00a7a7;
#   foreground: white;
#   bordercolor: #00a7a7
# }
# TButton::focus {
#   relief: flat;
#   background: #00a7a7;
#   foreground: white;
#   bordercolor: #00a7a7
# }
# TButton.focus {
#   relief: flat;
#   background: #00a7a7;
#   foreground: white;
#   bordercolor: #00a7a7
# }
# TButton focus {
#   relief: flat;
#   background: #00a7a7;
#   foreground: white;
#   bordercolor: #00a7a7
# }
# """)
#
# print(style.cssRules)
#
# rule: CSSStyleRule = style.cssRules[4]
# print(rule.selectorList)
# list_: SelectorList = rule.selectorList
# print(list_.seq)
# selector: Selector = list_.seq[0]
# print(selector.element)
# print(selector.seq)
# seq: Seq = selector.seq
# item: Item = seq[0]
# print(item.type)
#
# print(style.cssRules[1].selectorList.seq[0].seq[0].type)
# print(style.cssRules[2].selectorList.seq[0].seq[0].type)
# print(style.cssRules[3].selectorList.seq[0].seq[0].type)
# print(style.cssRules[4].selectorList.seq[0].seq[0].type)
#
# print(selector.specificity)
# print(rule.style)
#
# rule: CSSStyleRule = style.cssRules[0]
# print(rule.selectorList)
# list_: SelectorList = rule.selectorList
# print(list_.seq)
# print(rule.style)
#
# declaration: CSSStyleDeclaration = rule.style;
#
# for item in declaration:
#     # print(item)
#     print(f"  {repr(item.name)}: {repr(item.value)}")
#
# exit(1)
from socket import socket
from tkinter import ttk, filedialog, simpledialog, PhotoImage
from typing import Optional, Union, BinaryIO

from threadsafe_tkinter import Tk, Canvas, Frame, TclError

from old.client import Client
from old.downloader import Downloader
from old.gui import QCanvasButton, ScrolledWindow, DownloadItem, UploadItem, ErrorItem, CanvasItem, ColorType
from old.server import Server
from old.uploader import Uploader

ACCENT = "#00a7a7"

TREEVIEW_BG = "#7f7f7f"
TREEVIEW_FG = "#9f9f9f"
TREEVIEW_SEL_BG = "#00a7a7"
TREEVIEW_SEL_FG = "white"

BUTTON_BG = "#7f7f7f"
BUTTON_BG_FOC = "#00a7a7"
BUTTON_BG_DIS = "#5f5f5f"
BUTTON_FG = "#a7a7a7"
BUTTON_FG_FOC = "white"
BUTTON_FG_DIS = "#7f7f7f"
BUTTON_BD_COL = "#00a7a7"
BUTTON_RELIEF = "flat"
BUTTON_BD_WID = 0

ENTRY_BG = "#5f5f5f"
ENTRY_BG_FOC = "#00a7a7"
ENTRY_BG_DIS = "#7f7f7f"
ENTRY_FG = "#7f7f7f"
ENTRY_FG_FOC = "white"
ENTRY_FG_DIS = "#a7a7a7"
ENTRY_BD_COL = "#00a7a7"
ENTRY_RELIEF = "flat"
ENTRY_BD_WID = 0
ENTRY_SEL_BG = "#00c9c9"
ENTRY_SEL_BG_FOC = "#00dada"
ENTRY_SEL_BG_DIS = "#a7a7a7"
ENTRY_SEL_FG = "#7f7f7f"
ENTRY_SEL_FG_FOC = "white"
ENTRY_SEL_FG_DIS = "#ffffff"


class QCopyOverPC(Tk):
    """
    Main class for QCopyOverPC.
    @author: Quinten Jungblut
    """
    def __init__(self):
        self.connection: Optional[Union[Server, Client]] = None

        self.selectWindow = Tk()
        self.theme(self.selectWindow)

        self.selectWindow.wm_geometry("200x75")

        self.selectFrame = ttk.Frame(self.selectWindow)
        self.serverButton = ttk.Button(self.selectFrame, text="Server", command=lambda: self.select_server())
        self.clientButton = ttk.Button(self.selectFrame, text="Client", command=lambda: self.select_client())
        self.selectFrame.pack(fill="both", expand=True)

        self.serverButton.pack(fill="x", padx=5, pady=5)
        self.clientButton.pack(fill="x", padx=5, pady=5)

        self.selectWindow.mainloop()

        super(QCopyOverPC, self).__init__()

        if self.connection is not None:
            self.theme(self)

            self.frame = ttk.Frame()
            self.connStatus: Optional[str] = None

            self.radiframe = ttk.Frame(self)
            self.radiframe.pack()

            # Main frame.
            self.main_f = Frame(self.frame, background="#4f4f4f", height=500)
            self.main_f.pack(fill="both", expand=True)

            # Slots frame.
            self.s_frame = Frame(self.main_f, height=self.main_f.winfo_height() - 100, width=800)
            self.s_frame.pack(fill="y", expand=True)

            # Scrollwindow for the slots frame
            self.sw = ScrolledWindow(self.s_frame, 800, self.frame.winfo_height() + 0, expand=True,
                                     fill="both")

            self.sw.vbar.configure(bg="#575757", fg="#7f7f7f")

            # Configurate the canvas from the scrollwindow
            self.canv = self.sw.canvas
            self.canv.config(bg="#4f4f4f")

            # self.frame.
            self.frame_sw = self.sw.scroll_window
            self.frames = []

            # Defining the list of widgets
            self._id = {}
            # self.index = {}
            self.canvass = []
            self.buttons = []

            self.oldSelected: Optional[Canvas] = None
            self.selectedCanvas: Optional[Canvas] = None
            self._hoverCanvasOld: Optional[Canvas] = None
            self._hoverCanvas: Optional[Canvas] = None

            # titlefont = _utils.Font("Helvetica", 25, "bold")
            # infofont = _utils.Font("Helvetica", 16)

            # Get slots
            # if not os.path.exists(f"{_reg.Registry.gameData['launcherConfig']['gameDir']}saves/"):
            #     os.makedirs(f"{_reg.Registry.gameData['launcherConfig']['gameDir']}saves/")
            # names = os.listdir(f"{_reg.Registry.gameData['launcherConfig']['gameDir']}saves/")
            self.names = {}

            # # Information variables for each slot.
            # infos = {"dates": [], "score": [], "level": []}
            #
            # import time

            # self.item_info = names

            # Define the index variable.
            # i = 0

            # # Startloop
            # for name in names:
            #     i += 1

            self.frame.pack(fill="both", expand=True)

            self.openButton = QCanvasButton(self.frame, command=self.open, height=64)
            self.openButton.create_dynamictext(5, 5, text="Open File", anchor="nw", font=("helvetica", 16))
            self.openButton.create_dynamictext(5, 30, text="Open a file, and send it to all the connected clients", anchor="nw", font=("helvetica", 10))
            self.openButton.pack(fill="x", padx=5, pady=5)
            self.frame.pack(fill="both", expand=True)

            # Bahavior
            self.wm_protocol("WM_DELETE_WINDOW", lambda: self.destroy())
            self.wm_geometry("800x480")
            self.wm_title("Client" if self.connStatus == "client" else "Server")
            self.wm_iconphoto(False, PhotoImage(file="icon.png"))
            # self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file='icon.png'))

            # Size
            self.wm_minsize(800, 480)
            self.wm_resizable(False, True)

            # Mainloop
            self.mainloop()

            # Kill application process.
            os.kill(os.getpid(), 0)
        else:
            os.kill(os.getpid(), 0)

    def mainloop(self, n=None):
        """
        Application main loop.

        @param n: amount of loops.
        @author: Quinten Jungblut
        """
        try:
            while True:
                for uploader in self.connection.uploaders().copy():
                    uploader: Uploader
                    if not uploader.done:
                        try:
                            uploader.canvasItem.set_description(uploader.message)
                            # noinspection PyUnresolvedReferences
                            uploader.progressbar.config(maximum=uploader.fileSize, value=uploader.bytesSent)
                        except TclError:
                            uploader.done = True
                    if uploader.done:
                        self.connection.uploaders().remove(uploader)
                for downloader in self.connection.downloaders().copy():
                    downloader: Downloader
                    if not downloader.done:
                        try:
                            downloader.canvasItem.set_description(downloader.message)
                            # noinspection PyUnresolvedReferences
                            downloader.progressbar.config(maximum=downloader.fileSize, value=downloader.bytesReceived)
                        except TclError:
                            downloader.done = True
                    if downloader.done:
                        self.connection.downloaders().remove(downloader)
                self.update()
                self.update_idletasks()
        except TclError:
            return

    @staticmethod
    def on_complete(canvas, frames, progressbar, description=None, new_description=None):
        """
        On-complete callback.

        @param canvas: canvas
        @param frames: frames
        @param progressbar: the progressbar instance.
        @param description: the description.
        @param new_description: new description to display.
        """
        progressbar.destroy()

        if (description is not None) and (new_description is not None):
            canvas.itemconfig(description, text=new_description)

    @staticmethod
    def on_error(canvas: CanvasItem, progressbar, description, exc: Exception):
        """


        @param canvas:
        @param progressbar:
        @param description:
        @param exc:
        """
        progressbar.destroy()

        canvas.set_color(ColorType.ERROR)

        canvas.itemconfig(description, text=f"ERROR:\n    {exc.__class__.__name__}: {exc.__str__()}")

    def add_error_item(self, name, description):
        # titlefont = ("Helvetica", 20)
        # infofont = ("Helvetica", 10)

        self.frames.append(Frame(self.frame_sw, height=120, width=790, bg="#6f0000"))
        ErrorItem(self, name, description, height=120, width=790, bg="#6f0000", highlightthickness=0)
        self.canvass[-1].pack(fill="x")
        self.frames[-1].pack(fill="x")

    def add_file_upload(self, name, description, path):
        self.frames.append(Frame(self.frame_sw, height=150, width=790, bg="#6f6f6f"))

        item = UploadItem(self, name, description, height=150, width=790, bg="#6f6f6f", highlightthickness=0)
        item.onComplete = lambda canvas=item: self.on_complete(canvas, None, item.progressbar, item.desc, "Upload complete!")
        item.onError = lambda exc, _canv=item: self.on_error(_canv, item.progressbar, item.desc, exc)

        self.canvass[-1].pack(fill="x")
        self.frames[-1].pack(fill="x")

        self.connection.upload(
            path, item.progressbar,
            on_complete=lambda _canv=item: self.on_complete(
                _canv, None, item.progressbar, item.desc, "Upload complete!"),
            on_error=lambda exc, _canv=item: self.on_error(_canv, item.progressbar, item.desc, exc), canvas_item=item)

    def add_file_download(self, conn: socket, name, description, path):
        self.frames.append(Frame(self.frame_sw, height=150, width=790, bg="#6f6f6f"))

        item = DownloadItem(self, name, description, height=150, width=790, bg="#6f6f6f", highlightthickness=0)
        item.onComplete = lambda canvas=item:  self.on_complete(canvas, None, item.progressbar, item.desc, "Download complete!")
        item.onError = lambda exc, _canv=item: self.on_error(_canv, item.progressbar, item.desc, exc)

        self.canvass[-1].pack(fill="x")
        self.frames[-1].pack(fill="x")

        self.connection.download(
            conn, path, item.progressbar,
            on_complete=lambda canvas=item: self.on_complete(
                canvas, None, item.progressbar, item.desc, "Download complete!"),
            on_error=lambda exc, _canv=item: self.on_error(_canv, item.progressbar, item.desc, exc), canvas_item=item)

    def add_folder_upload(self, name, description, path):
        self.frames.append(Frame(self.frame_sw, height=150, width=790, bg="#6f6f6f"))

        item = UploadItem(self, name, description, height=150, width=790, bg="#6f6f6f", highlightthickness=0)
        item.onComplete = lambda canvas=item: self.on_complete(canvas, None, item.progressbar, item.desc, "Upload complete!")
        item.onError = lambda exc, _canv=item: self.on_error(_canv, item.progressbar, item.desc, exc)

        self.canvass[-1].pack(fill="x")
        self.frames[-1].pack(fill="x")

        self.connection.upload_folder(
            path, item.progressbar,
            on_complete=lambda _canv=item: self.on_complete(
                _canv, None, item.progressbar, item.desc, "Upload complete!"),
            on_error=lambda exc, _canv=item: self.on_error(_canv, item.progressbar, item.desc, exc), canvas_item=item)

    def add_folder_download(self, conn: socket, name, description, path):
        self.frames.append(Frame(self.frame_sw, height=150, width=790, bg="#6f6f6f"))

        item = DownloadItem(self, name, description, height=150, width=790, bg="#6f6f6f", highlightthickness=0)
        item.onComplete = lambda canvas=item:  self.on_complete(canvas, None, item.progressbar, item.desc, "Download complete!")
        item.onError = lambda exc, _canv=item: self.on_error(_canv, item.progressbar, item.desc, exc)

        self.canvass[-1].pack(fill="x")
        self.frames[-1].pack(fill="x")

        self.connection.download_folder(
            conn, path, item.progressbar,
            on_complete=lambda canvas=item: self.on_complete(
                canvas, None, item.progressbar, item.desc, "Download complete!"),
            on_error=lambda exc, _canv=item: self.on_error(_canv, item.progressbar, item.desc, exc), canvas_item=item)

    def _on_canv_leave(self, hover_canvas):
        """
        Canvas-leave event handler.

        :param hover_canvas:
        :return:
        """

        # if self._hoverCanvasOld is not None:
        #     if self.selectedCanvas != self._hoverCanvasOld:
        #         self._hoverCanvasOld.config(bg="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Title"], fill="#a7a7a7")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Filename"], fill="#a7a7a7")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Description"], fill="#a7a7a7")
        #         # for subid in self._id[self._hoverCanvasOld]["Infos"]:
        #         #     self._hoverCanvasOld.itemconfig(subid, fill="#a7a7a7")
        #     else:
        #         self._hoverCanvasOld.config(bg="#4f4f4f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Title"], fill="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Filename"], fill="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Description"], fill="#7f7f7f")
        #         # for subid in self._id[self._hoverCanvasOld]["Infos"]:
        #         #     self._hoverCanvasOld.itemconfig(subid, fill="#00a7a7")
        # self._hoverCanvasOld = None

    def _on_canv_motion(self, hover_canvas):
        """
        Canvas-motion event handler.

        :param hover_canvas:
        :return:
        """

        # if self._hoverCanvasOld == hover_canvas:
        #     return
        # if self._hoverCanvasOld is not None:
        #     if self.selectedCanvas != self._hoverCanvasOld:
        #         self._hoverCanvasOld.config(bg="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Title"], fill="#a7a7a7")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Filename"], fill="#a7a7a7")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Description"], fill="#a7a7a7")
        #         # for subid in self._id[self._hoverCanvasOld]["Infos"]:
        #         #     self._hoverCanvasOld.itemconfig(subid, fill="#939393")
        #     else:
        #         self._hoverCanvasOld.config(bg="#4f4f4f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Title"], fill="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Filename"], fill="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Description"], fill="#7f7f7f")
        #         # for subid in self._id[self._hoverCanvasOld]["Infos"]:
        #         #     self._hoverCanvasOld.itemconfig(subid, fill="#00a7a7")
        # self._hoverCanvasOld = hover_canvas
        #
        # if hover_canvas != self.selectedCanvas:
        #     hover_canvas.config(bg="#a7a7a7")
        #     hover_canvas.itemconfig(self._id[hover_canvas]["Title"], fill="#ffffff")
        #     hover_canvas.itemconfig(self._id[hover_canvas]["Filename"], fill="#ffffff")
        #     hover_canvas.itemconfig(self._id[hover_canvas]["Description"], fill="#ffffff")
        #     # for subid in self._id[hover_canvas]["Infos"]:
        #     #     hover_canvas.itemconfig(subid, fill="#dadada")
        # else:
        #     hover_canvas.config(bg="#4f4f4f")
        #     hover_canvas.itemconfig(self._id[hover_canvas]["Title"], fill="#7f7f7f")
        #     hover_canvas.itemconfig(self._id[hover_canvas]["Filename"], fill="#7f7f7f")
        #     hover_canvas.itemconfig(self._id[hover_canvas]["Description"], fill="#7f7f7f")
        #     # for subid in self._id[hover_canvas]["Infos"]:
        #     #     hover_canvas.itemconfig(subid, fill="#00dada")
        # self._hoverCanvas = hover_canvas

    def _on_canv_lclick(self, c: Canvas):
        """
        Canvas-leftclick event handler.

        :param c:
        :return:
        """

        # if self.oldSelected is not None:
        #     self.oldSelected.config(bg="#7f7f7f")
        #     self.oldSelected.itemconfig(self._id[self.oldSelected]["Title"], fill="#a7a7a7")
        #     self.oldSelected.itemconfig(self._id[self.oldSelected]["Filename"], fill="#a7a7a7")
        #     self.oldSelected.itemconfig(self._id[self.oldSelected]["Description"], fill="#a7a7a7")
        #     # for subid in self._id[self.oldSelected]["Infos"]:
        #     #     self.oldSelected.itemconfig(subid, fill="#939393")
        # self.oldSelected = c
        #
        # c.config(bg="#00a7a7")
        # c.itemconfig(self._id[c]["Title"], fill="#ffffff")
        # c.itemconfig(self._id[c]["Filename"], fill="#a7a7a7")
        # c.itemconfig(self._id[c]["Description"], fill="#a7a7a7")
        # # for subid in self._id[c]["Infos"]:
        # #     c.itemconfig(subid, fill="#00dada")
        #
        # self.selectedCanvas = c

    def select_server(self):
        self.connection = Server(self)
        self.connection.start()
        self.selectWindow.destroy()
        # self.wm_attributes("-alpha", 1)

    def select_client(self):
        host = simpledialog.askstring("Host IP Adress", "Enter the server IP adress.")

        self.connection = Client(host, self)
        self.connection.start()
        self.selectWindow.destroy()
        # self.wm_attributes("-alpha", 1)

    def on_radioclick(self, evt):
        if evt.widget == self.serverRadioBtn:
            self.serverRadioBtn.state(["selected", "!alternate", "!pressed"])
            self.clientRadioBtn.state(["!selected", "!alternate", "!pressed"])
            self.connStatus = "server"
        if evt.widget == self.clientRadioBtn:
            self.clientRadioBtn.state(["selected", "!alternate", "!pressed"])
            self.serverRadioBtn.state(["!selected", "!alternate", "!pressed"])
            self.connStatus = "client"

        # print(self.serverRadioBtn.state())
        return "break"

    def savefile(self, conn: socket, filename, data):
        # Ask for a folder.
        f: str = filedialog.askdirectory(title=f"Save File: {filename}", mustexist=True)
        path: str = os.path.join(f, filename)

        # Return if no folder is selected.
        if path is None:
            return
        if path == "":
            return

        self.add_file_download(conn, data["filename"], "Download in queue...", path)

    def open(self):
        self.selectWindow = Tk()
        self.theme(self.selectWindow)

        self.selectWindow.wm_geometry("200x75")

        self.selectFrame = ttk.Frame(self.selectWindow)
        self.serverButton = ttk.Button(self.selectFrame, text="File", command=lambda: self.openfile())
        self.clientButton = ttk.Button(self.selectFrame, text="Folder", command=lambda: self.openfolder())
        self.selectFrame.pack(fill="both", expand=True)

        self.serverButton.pack(fill="x", padx=5, pady=5)
        self.clientButton.pack(fill="x", padx=5, pady=5)

        self.selectWindow.mainloop()


    def openfile(self):
        # Return if there's no connection.
        if self.connection is None:
            return

        # Return if there's already a upload
        if len(self.connection.uploaders()) >= 1:
            return

        # Ask for file to upload.
        files = [('Any File', f'*.*')]
        f: BinaryIO = filedialog.askopenfile("rb", title="Open File for Upload...", filetypes=files)

        # Return if no file is opened.
        if f is None:
            return

        # Reset file-index.
        f.seek(0)

        # Send if has connection.
        if self.connection:
            # Data to send
            data_send = {"type": "file", "filename": os.path.split(str(f.name))[-1]}

            # Queue the upload
            self.connection.up_queue_all(data_send)

            # Add item
            self.add_file_upload(data_send["filename"], "Upload in queue...", f.name)
            del data_send

    def openfolder(self):
        # Return if there's no connection.
        if self.connection is None:
            return

        # Return if there's already a upload.
        if len(self.connection.uploaders()) >= 1:
            return

        # Ask for folder to upload.
        files = [('Any File', f'*.*')]
        f: str = filedialog.askdirectory(title=f"Open Folder for Upload...", mustexist=True)

        # Return if no folder is selected.
        if f is None:
            return
        if f == "":
            return

        # Send if has connection.
        if self.connection:
            # Data to send
            data_send = {"type": "folder", "name": os.path.split(str(f))[-1]}

            # Queue the upload
            self.connection.up_queue_all(data_send)

            # Add item
            self.add_folder_upload(data_send["filename"], "Upload in queue...", f)
            del data_send

    def do(self, conn: socket, data: object):
        # print(data)
        if type(data) == dict:
            data: dict

            # Check type for file.
            if data["type"] == "file":
                self.savefile(conn, data["filename"], data)
            elif data["type"] == "folder":
                self.savefolder(conn, data["name"], data)

    @staticmethod
    def theme(widget=None):
        c_font_t = ("helvetica", 11)

        # Initializing the theme for the options menu.
        style = ttk.Style(widget)
        style.theme_settings("default", {
            "TEntry": {
                "configure": {"font": c_font_t, "relief": "flat", "selectborderwidth": 0, "padding": 10},
                "map": {
                    "relief": [("active", ENTRY_RELIEF),
                               ("focus", ENTRY_RELIEF),
                               ("!disabled", ENTRY_RELIEF)],
                    "bordercolor": [("active", ENTRY_BD_COL),
                                    ("focus", ENTRY_BD_COL),
                                    ("!disabled", ENTRY_BD_COL)],
                    "background": [("active", ENTRY_BG),
                                   ("focus", ENTRY_BG_FOC),
                                   ("!disabled", ENTRY_BG_DIS)],
                    "fieldbackground": [("active", ENTRY_BG),
                                        ("focus", ENTRY_BG_FOC),
                                        ("!disabled", ENTRY_BG_DIS)],
                    "foreground": [("active", ENTRY_FG),
                                   ("focus", ENTRY_FG_FOC),
                                   ("!disabled", ENTRY_FG_DIS)],
                    "selectbackground": [("active", ENTRY_SEL_BG),
                                         ("focus", ENTRY_SEL_BG_FOC),
                                         ("!disabled", ENTRY_SEL_BG_DIS)],
                    "selectforeground": [("active", ENTRY_SEL_FG),
                                         ("focus", ENTRY_SEL_FG_FOC),
                                         ("!disabled", ENTRY_SEL_FG_DIS)]
                }
            },
            "TFrame": {
                "configure": {"background": "#5f5f5f", "relief": "flat"}
            },

            "TProgressbar": {
                "configure": {"background": ACCENT,
                              "bordercolor": ACCENT,
                              "troughcolor": "#7f7f7f"}
            },
            "TLabel": {
                "configure": {"background": "#5f5f5f",
                              "foreground": "#7f7f7f",
                              "font": c_font_t}
            },
            "TButton": {
                "configure": {"font": c_font_t, "relief": BUTTON_RELIEF, "bd": 1},
                "map": {
                    "background": [("active", BUTTON_BG_FOC),
                                   ("focus", BUTTON_BG),
                                   ("!disabled", BUTTON_BG)],
                    "bordercolor": [("active", BUTTON_BD_COL),
                                    ("focus", BUTTON_BG_FOC),
                                    ("!disabled", BUTTON_BD_COL)],
                    "foreground": [("active", BUTTON_FG_FOC),
                                   ("focus", BUTTON_FG_FOC),
                                   ("!disabled", BUTTON_FG)],
                }
            },
            "Treeview": {
                "configure": {"padding": 0, "font": c_font_t, "relief": "flat", "border": 0,
                              "rowheight": 24},
                "map": {
                    "background": [("active", TREEVIEW_BG),
                                   ("focus", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_BG),
                                   ("selected", TREEVIEW_BG)],
                    "fieldbackground": [("active", TREEVIEW_BG),
                                        ("focus", TREEVIEW_BG),
                                        ("!disabled", TREEVIEW_BG)],
                    "foreground": [("active", TREEVIEW_FG),
                                   ("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_FG),
                                   ("selected", TREEVIEW_FG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            },
            "Treeview.Item": {
                "configure": {"padding": 0},
                "map": {
                    "background": [("active", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_SEL_BG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "fieldbackground": [("!disabled", TREEVIEW_SEL_BG),
                                        ("active", TREEVIEW_SEL_BG),
                                        ("!selected", TREEVIEW_SEL_BG)],
                    "foreground": [("active", TREEVIEW_SEL_BG),
                                   ("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_SEL_FG),
                                   ("selected", TREEVIEW_SEL_BG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            },
            "Treeview.Cell": {
                "configure": {"padding": 0},
                "map": {
                    "background": [("active", TREEVIEW_SEL_BG),
                                   ("!disabled", TREEVIEW_SEL_BG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "fieldbackground": [("!disabled", TREEVIEW_SEL_BG),
                                        ("active", TREEVIEW_SEL_BG),
                                        ("!selected", TREEVIEW_SEL_BG)],
                    "foreground": [("focus", TREEVIEW_SEL_FG),
                                   ("!disabled", TREEVIEW_SEL_FG),
                                   ("!selected", TREEVIEW_SEL_BG)],
                    "relief": [("focus", "flat"),
                               ("active", "flat"),
                               ("!disabled", "flat")]
                }
            }
        })
        # print(style.map("Treeview"))
        # print(style.configure("Treeview"))
        # print(style.co("Treeview"))

        # style.configure("BW.TTreeview", foreground=", background="white")
        #
        # foreground = "black", background = "white"
        # sty
        style.theme_use("default")
        style.configure('TEntry', relief='flat', bd=0, borderwidth=0)

        # print(style.layout("TEntry"))

        #   lets try to change this structure
        style.layout('TEntry', [
            ('Entry.highlight', {
                "border": 0,
                'sticky': 'nswe',
                'children': [('Entry.border', {
                    'border': 0,
                    'sticky': 'nswe',
                    'children':
                        [('Entry.padding', {
                            'sticky': 'nswe',
                            'children':
                                [('Entry.textarea', {
                                    'sticky': 'nswe',
                                    "border": 0})]
                        })]
                }), ('Entry.bd', {
                    'sticky': 'nswe',
                    'children': [(
                        'Entry.padding', {
                            'sticky': 'nswe',
                            'children': [(
                                'Entry.textarea', {
                                    'sticky': 'nswe'})]
                        })],
                    'border': 0})
                             ]
            })])
        style.configure('TEntry', relief='flat', bd=0)
        style.configure("TProgressbar", dtroughrelief="flat", borderwidth=0, thickness=10)


if __name__ == '__main__':
    import sys
    if hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        os.chdir(sys._MEIPASS)

    window = QCopyOverPC()
