import os
from threading import Thread
from time import sleep
from tkinter import Tk, ttk, filedialog, simpledialog
from typing import Optional, Union

from advUtils import network
from advUtils.network import PacketSystem

TREEVIEW_BG = "#7f7f7f"
TREEVIEW_FG = "#9f9f9f"
TREEVIEW_SEL_BG = "#00a7a7"
TREEVIEW_SEL_FG = "white"

BUTTON_BG = "#7f7f7f"
BUTTON_BG_FOC = "#00a7a7"
BUTTON_BG_DIS = "#5c5c5c"
BUTTON_FG = "#a7a7a7"
BUTTON_FG_FOC = "white"
BUTTON_FG_DIS = "#7f7f7f"
BUTTON_BD_COL = "#00a7a7"
BUTTON_RELIEF = "flat"
BUTTON_BD_WID = 0

ENTRY_BG = "#5c5c5c"
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


class Server(network.Server):
    def __init__(self, window):
        super(Server, self).__init__(43393)
        # self._queue = Queue()
        self._queue = []

        self.window: QCopyOverPC = window

    def queue(self, data):
        self._queue.append(data)

    def reciever(self, conn):
        pak = PacketSystem(conn)

        try:
            while True:
                sleep(0.1)
                # if not self._queue:
                #     continue
                recieved = pak.recv()
                if recieved is not None:
                    self.window.do(recieved)
        except ConnectionResetError:
            pass
        except ConnectionRefusedError:
            pass
        except ConnectionAbortedError:
            pass

    def runner(self, conn, secret):
        Thread(target=lambda: self.sender(conn)).start()
        Thread(target=lambda: self.reciever(conn)).start()

    def sender(self, conn):
        pak = PacketSystem(conn)

        try:
            while True:
                sleep(0.1)
                if not self._queue:
                    continue
                data = self._queue.pop(0)
                # print(data)
                if data:
                    pak.sendall(data)
        except ConnectionResetError:
            pass
        except ConnectionRefusedError:
            pass
        except ConnectionAbortedError:
            pass


class Client(network.Client):
    def __init__(self, host, window):
        super(Client, self).__init__(host, 43393)
        self._queue = []

        self.window: QCopyOverPC = window

    def queue(self, data):
        self._queue.append(data)

    def reciever(self, conn):
        pak = PacketSystem(conn)

        try:
            while True:
                sleep(0.1)
                # if not self._queue:
                #     continue
                recieved = pak.recv()
                if recieved is not None:
                    self.window.do(recieved)
        except ConnectionResetError:
            pass
        except ConnectionRefusedError:
            pass
        except ConnectionAbortedError:
            pass

    def runner(self, conn, secret):
        Thread(target=lambda: self.sender(conn)).start()
        Thread(target=lambda: self.reciever(conn)).start()

    def sender(self, conn):
        pak = PacketSystem(conn)

        try:
            while True:
                sleep(0.1)
                if not self._queue:
                    continue
                data = self._queue.pop(0)
                # print(data)
                if data:
                    pak.sendall(data)
        except ConnectionResetError:
            pass
        except ConnectionRefusedError:
            pass
        except ConnectionAbortedError:
            pass


class QCopyOverPC(Tk):
    def __init__(self):
        self.connection: Optional[Union[Server, Client]] = None

        self.selectWindow = Tk()
        self.theme(self.selectWindow)

        c_font_t = ("helvetica", 10)

        self.selectWindow.wm_geometry("200x150")

        self.selectFrame = ttk.Frame(self.selectWindow)
        self.serverButton = ttk.Button(self.selectFrame, text="Server", command=lambda: self.select_server())
        self.clientButton = ttk.Button(self.selectFrame, text="Client", command=lambda: self.select_client())
        self.selectFrame.pack(fill="both", expand=True)

        self.serverButton.pack(fill="x", padx=2, pady=2)
        self.clientButton.pack(fill="x", padx=2, pady=2)

        self.selectWindow.mainloop()

        super(QCopyOverPC, self).__init__()

        if self.connection is not None:
            self.theme(self)

            self.frame = ttk.Frame()
            self.connStatus: Optional[str] = None

            self.radioFrame = ttk.Frame(self)
            # self.serverRadioBtn = ttk.Radiobutton(self.radioFrame, text="Server")
            # self.clientRadioBtn = ttk.Radiobutton(self.radioFrame, text="Client")
            # self.serverRadioBtn.bind("<ButtonRelease-1>", self.on_radioclick)
            # self.clientRadioBtn.bind("<ButtonRelease-1>", self.on_radioclick)
            # self.serverRadioBtn.pack()
            # self.clientRadioBtn.pack()
            self.radioFrame.pack()

            self.openButton = ttk.Button(self.frame, text="Open", command=self.openfile)
            self.openButton.pack(fill="x", padx=2, pady=2)
            self.frame.pack(fill="both", expand=True)
            # self.wm_attributes("-alpha", 0)

            self.wm_protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), 0))
            self.wm_geometry("200x150")

            self.mainloop()
        else:
            os.kill(os.getpid(), 0)

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

    def savefile(self, filename, data):
        # files = [('Unknown FileType', f'*{os.path.splitext(filename)[-1]}')]
        # f = filedialog.asksaveasfile(filetypes=files, mode='wb', defaultextension=os.path.splitext(filename)[-1])
        f = filedialog.askdirectory(title=f"Save File: {filename}", mustexist=True)
        path = os.path.join(f, filename)

        with open(path, "wb+") as file:
            file.write(data)
        # print(f)
        # f.write(data)

    def openfile(self):
        if self.connection is None:
            return

        files = [('Any File', f'*.*')]
        f = filedialog.askopenfile("rb", title="Open File", filetypes=files)
        f.seek(0)
        # f.read()

        if self.connection:
            a = {"type": "file", "filename": os.path.split(str(f.name))[-1], "content": f.read()}
            self.connection.queue(a)
            # print(a)
            del a

    def do(self, data):
        # print(data)
        if data["type"] == "file":
            self.savefile(data["filename"], data["content"])

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
                "configure": {"background": "#5c5c5c", "relief": "flat"}
            },

            "TLabel": {
                "configure": {"background": "#5c5c5c",
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


# cb.OpenClipboard()
#
# if cb.IsClipboardFormatAvailable(cb.CF_HDROP):
#     clipboard_file_path = cb.GetClipboardData(cb.CF_HDROP)
#     print(clipboard_file_path)
#
# cb.CloseClipboard()

if __name__ == '__main__':
    window = QCopyOverPC()
    # window.savefile("hello.txt", b"Hoi")
    # window.openfile()
