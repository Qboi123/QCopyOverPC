import os
import shutil
from pickle import UnpicklingError
from socket import socket
from threading import Thread
from time import sleep
from tkinter import ttk, filedialog, simpledialog, PhotoImage
from tkinter.ttk import Progressbar
from typing import Optional, Union, List, Any, Callable

from advUtils import network
from advUtils.network import PacketSystem
from threadsafe_tkinter import Tk, Canvas, Frame, TclError

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


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class CustomVerticalScrollbar(Canvas):
    def __init__(self, parent, **kwargs):
        """
        Custom scrollbar, using canvas. It can be configured with fg, bg and command

        :param parent:
        :param kwargs:
        """

        self.command = kwargs.pop("command", None)
        kw = kwargs.copy()
        bd = 0
        hlt = 0
        if "fg" in kw.keys():
            del kw["fg"]
        if "bd" in kw.keys():
            bd = kw.pop("bd")
        if "border" in kw.keys():
            bd = kw.pop("border")
        if "highlightthickness" in kw.keys():
            hlt = kw.pop("highlightthickness")
        Canvas.__init__(self, parent, **kw, highlightthickness=hlt, border=bd, bd=bd)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"

        # coordinates are irrelevant; they will be recomputed
        # in the 'set' method\
        self.old_y = 0
        self._id = self.create_rectangle(0, 0, 1, 1, fill=kwargs["fg"], outline=kwargs["fg"], tags=("thumb",))
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def configure(self, cnf=None, **kwargs):
        command = kwargs.pop("command", None)
        self.command = command if command is not None else self.command
        kw = kwargs.copy()
        if "fg" in kw.keys():
            del kw["fg"]
        super().configure(**kw, highlightthickness=0, border=0, bd=0)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"
        self.itemconfig(self._id, fill=kwargs["fg"], outline=kwargs["fg"])

    def config(self, cnf=None, **kwargs):
        self.configure(cnf, **kwargs)

    def redraw(self, event):
        # The command is presumably the `yview` method of a widget.
        # When called without any arguments it will return fractions
        # which we can pass to the `set` command.
        self.set(*self.command())

    def set(self, first, last):
        first = float(first)
        last = float(last)
        height = self.winfo_height()
        x0 = int(self.cget("bd"))
        x1 = self.winfo_width() - int(self.cget("bd"))
        y0 = max(int(height * first), 0)
        y1 = min(int(height * last), height)
        self._x0 = x0
        self._x1 = x1
        self._y0 = y0
        self._y1 = y1

        self.coords("thumb", x0, y0, x1, y1)

    def on_press(self, event):
        self.bind("<Motion>", self.on_click)
        self.pressed_y = event.y
        self.on_click(event)

    def on_release(self, event):
        self.unbind("<Motion>")

    def on_click(self, event):
        y = event.y / self.winfo_height()
        y0 = self._y0
        y1 = self._y1
        a = y + ((y1 - y0) / -(self.winfo_height() * 2))
        self.command("moveto", a)


# noinspection PyAttributeOutsideInit,PyUnusedLocal
class CustomHorizontalScrollbar(Canvas):
    def __init__(self, parent, **kwargs):
        """
        Custom scrollbar, using canvas. It can be configured with fg, bg and command

        :param parent:
        :param kwargs:
        """

        self.command = kwargs.pop("command", None)
        kw = kwargs.copy()
        bd = 0
        hlt = 0
        if "fg" in kw.keys():
            del kw["fg"]
        if "bd" in kw.keys():
            bd = kw.pop("bd")
        if "border" in kw.keys():
            bd = kw.pop("border")
        if "highlightthickness" in kw.keys():
            hlt = kw.pop("highlightthickness")
        Canvas.__init__(self, parent, **kw, highlightthickness=hlt, border=bd, bd=bd)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"

        # coordinates are irrelevant; they will be recomputed
        # in the 'set' method\
        self.old_y = 0
        self._id = self.create_rectangle(0, 0, 1, 1, fill=kwargs["fg"], outline=kwargs["fg"], tags=("thumb",))
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def configure(self, cnf=None, **kwargs):
        command = kwargs.pop("command", None)
        self.command = command if command is not None else self.command
        kw = kwargs.copy()
        if "fg" in kw.keys():
            del kw["fg"]
        super().configure(**kw, highlightthickness=0, border=0, bd=0)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"
        self.itemconfig(self._id, fill=kwargs["fg"], outline=kwargs["fg"])

    def config(self, cnf=None, **kwargs):
        self.configure(cnf, **kwargs)

    def redraw(self, event):
        # The command is presumably the `yview` method of a widget.
        # When called without any arguments it will return fractions
        # which we can pass to the `set` command.
        self.set(*self.command())

    def set(self, first, last):
        first = float(first)
        last = float(last)
        width = self.winfo_width()
        y0 = 1
        y1 = self.winfo_width() - 1
        x0 = max(int(width * first), 0)
        x1 = min(int(width * last), width)
        self._x0 = x0
        self._x1 = x1
        self._y0 = y0
        self._y1 = y1

        self.coords("thumb", x0, y0, x1, y1)

    def on_press(self, event):
        self.bind("<Motion>", self.on_click)
        self.pressed_x = event.x
        self.on_click(event)

    def on_release(self, event):
        self.unbind("<Motion>")

    def on_click(self, event):
        x = event.x / self.winfo_width()
        x0 = self._x0
        x1 = self._x1
        a = x + ((x1 - x0) / -(self.winfo_width() * 2))
        self.command("moveto", a)


# noinspection PyUnusedLocal
class ScrolledWindow(Frame):
    """
    1. Master widget gets scrollbars and a canvas. Scrollbars are connected
    to canvas scrollregion.

    2. self.scrollwindow is created and inserted into canvas

    Usage Guideline:
    Assign any widgets as children of <ScrolledWindow instance>.scrollwindow
    to get them inserted into canvas

    __init__(self, parent, canv_w = 400, canv_h = 400, *args, **kwargs)
    docstring:
    Parent = master of scrolled window
    canv_w - width of canvas
    canv_h - height of canvas

    """

    def __init__(self, parent, canv_w=400, canv_h=400, expand=False, fill=None, height=None, width=None, *args,
                 scrollcommand=lambda: None, scrollbarbg=None, scrollbarfg="darkgray", **kwargs):
        """Parent = master of scrolled window
        canv_w - width of canvas
        canv_h - height of canvas

       """
        super().__init__(parent, height=canv_h, width=canv_w, *args, **kwargs)

        self.parent = parent
        self.scrollCommand = scrollcommand

        # creating a scrollbars

        if width is None:
            __width = 0
        else:
            __width = width

        if height is None:
            __height = 0
        else:
            __height = width

        self.canv = Canvas(self.parent, bg='#FFFFFF', width=canv_w, height=canv_h,
                           scrollregion=(0, 0, __width, __height), highlightthickness=0)

        self.vbar = CustomVerticalScrollbar(self.parent, width=10, command=self.canv.yview, bg=scrollbarbg, fg=scrollbarfg, bd=0)
        self.canv.configure(yscrollcommand=self.vbar.set)

        self.vbar.pack(side="right", fill="y")
        self.canv.pack(side="left", fill=fill, expand=expand)

        # creating a frame to inserto to canvas
        self.scrollwindow = Frame(self.parent, height=height, width=width)

        self.scrollwindow2 = self.canv.create_window(0, 0, window=self.scrollwindow, anchor='nw', height=height,
                                                     width=width)

        self.canv.config(  # xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
            scrollregion=(0, 0, canv_h, canv_w))

        self.scrollwindow.bind('<Configure>', self._configure_window)
        self.scrollwindow.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollwindow.bind('<Leave>', self._unbound_to_mousewheel)

        return

    def _bound_to_mousewheel(self, event):
        self.canv.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canv.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")
        # self.scrollCommand(int(-1 * (event.delta / 120)), self.scrollwindow.winfo_reqheight(), self.vbar.get(),
        # self.vbar)

    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scrollwindow.winfo_reqwidth(), self.scrollwindow.winfo_reqheight() + 1)
        self.canv.config(scrollregion='0 0 %s %s' % size)
        # if self.scrollwindow.winfo_reqwidth() != self.canv.winfo_width():
        #     # update the canvas's width to fit the inner frame
        #     # self.canv.config(width=self.scrollwindow.winfo_reqwidth())
        # if self.scrollwindow.winfo_reqheight() != self.canv.winfo_height():
        #     # update the canvas's width to fit the inner frame
        #     # self.canv.config(height=self.scrollwindow.winfo_reqheight())


class Server(network.Server):
    def __init__(self, window_):
        super(Server, self).__init__(43393)
        self._queue = []
        self._queue2 = []

        self.window: QCopyOverPC = window_
        self._uploaders: List[Uploader] = []
        self._downloaders: List[Downloader] = []

    def queue(self, data):
        self._queue.append(data)

    def queue2(self, data):
        self._queue2.append(data)

    def upload(self, path, progressbar, *, on_complete=lambda: None, on_error=lambda exc: None):
        self.queue(PreUploader(path, progressbar, on_complete=on_complete, on_error=on_error))

    def download(self, path, progressbar, *, on_complete=lambda: None, on_error=lambda exc: None):
        self.queue2(PreDownloader(path, progressbar, on_complete=on_complete, on_error=on_error))

    def uploaders(self):
        return self._uploaders

    def downloaders(self):
        return self._downloaders

    def reciever(self, conn):
        pak = PacketSystem(conn)

        try:
            while True:
                sleep(0.1)
                # if not self._queue:
                #     continue
                if not self._downloaders:
                    recieved = pak.recv()
                    if recieved is not None:
                        self.window.do(recieved)
                    if not self._queue2:
                        continue
                    data = self._queue2.pop(0)
                    if isinstance(data, PreDownloader):
                        self._downloaders.append(data.get_downloader(conn))
                        continue
        except ConnectionResetError:
            pass
        except ConnectionRefusedError:
            pass
        except ConnectionAbortedError:
            pass
        except OverflowError:
            Thread(target=lambda: self.reciever(conn)).start()
        except MemoryError:
            Thread(target=lambda: self.reciever(conn)).start()
        except UnpicklingError:
            Thread(target=lambda: self.reciever(conn)).start()

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
                if isinstance(data, PreUploader):
                    self._uploaders.append(data.get_uploader(conn))
                    continue
                # print(data)
                if data:
                    pak.sendall(data)
        except ConnectionResetError:
            pass
        except ConnectionRefusedError:
            pass
        except ConnectionAbortedError:
            pass


class PreUploader(object):
    def __init__(self, path, progressbar, *, on_complete=lambda: None, on_error=lambda exc: None):
        self.path = path
        self.progressbar = progressbar

        self.on_error = on_error
        self.on_complete = on_complete

    def get_uploader(self, conn):
        a = Uploader(conn, self.path, self.progressbar, on_complete=self.on_complete, on_error=self.on_error)
        a.start()
        return a


class PreDownloader(object):
    def __init__(self, path, progressbar, *, on_complete=lambda: None, on_error=lambda exc: None):
        self.path = path
        self.progressbar = progressbar

        self.on_error = on_error
        self.on_complete = on_complete

    def get_downloader(self, conn):
        a = Downloader(conn, self.path, self.progressbar, on_complete=self.on_complete, on_error=self.on_error)
        a.start()
        return a


class Client(network.Client):
    def __init__(self, host, window_):
        super(Client, self).__init__(host, 43393)
        self._queue = []
        self._queue2 = []

        self.window: QCopyOverPC = window_
        self._uploaders: List[Uploader] = []
        self._downloaders: List[Downloader] = []

    def queue(self, data):
        self._queue.append(data)

    def queue2(self, data):
        self._queue2.append(data)

    def upload(self, path, progressbar, *, on_complete=lambda: None, on_error=lambda exc: None):
        self.queue(PreUploader(path, progressbar, on_complete=on_complete, on_error=on_error))

    def download(self, path, progressbar, *, on_complete=lambda: None, on_error=lambda exc: None):
        self.queue2(PreDownloader(path, progressbar, on_complete=on_complete, on_error=on_error))

    def uploaders(self):
        return self._uploaders

    def downloaders(self):
        return self._downloaders

    def reciever(self, conn):
        pak = PacketSystem(conn)

        try:
            while True:
                sleep(0.1)
                # if not self._queue:
                #     continue
                if not self._downloaders:
                    recieved = pak.recv()
                    if recieved is not None:
                        self.window.do(recieved)
                    if not self._queue2:
                        continue
                    data = self._queue2.pop(0)
                    if isinstance(data, PreDownloader):
                        self._downloaders.append(data.get_downloader(conn))
                        continue
        except ConnectionResetError:
            pass
        except ConnectionRefusedError:
            pass
        except ConnectionAbortedError:
            pass
        except MemoryError:
            Thread(target=lambda: self.reciever(conn)).start()
        except OverflowError:
            Thread(target=lambda: self.reciever(conn)).start()
        except UnpicklingError:
            Thread(target=lambda: self.reciever(conn)).start()

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
                if isinstance(data, PreUploader):
                    self._uploaders.append(data.get_uploader(conn))
                    continue
                # print(data)
                if data:
                    pak.sendall(data)
        except ConnectionResetError:
            pass
        except ConnectionRefusedError:
            pass
        except ConnectionAbortedError:
            pass


class QCanvasButton(Canvas):
    def __init__(self, master, height=40, width=80, command=lambda: None):
        super(QCanvasButton, self).__init__(master, bg="#7f7f7f", height=height, width=width, highlightthickness=0)

        self._hovered = False
        self._pressed = False
        self._command = command
        self._texts = []
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, evt):
        if evt.widget == self:
            self.config(bg="#00afaf")
            for id_ in self._texts:
                self.itemconfigure(id_, fill="#ffffff")
            self._hovered = True

    def _on_leave(self, evt):
        if evt.widget == self:
            self.config(bg="#6f6f6f")
            for id_ in self._texts:
                self.itemconfigure(id_, fill="#9f9f9f")
            self._hovered = False

    def _on_press(self, evt):
        if evt.widget == self:
            self.config(bg="#4f4f4f")
            for id_ in self._texts:
                self.itemconfigure(id_, fill="#676767")
            self._pressed = True

    def _on_release(self, evt):
        if self._hovered:
            self.config(bg="#00afaf")
            self._command()
            for id_ in self._texts:
                self.itemconfigure(id_, fill="#ffffff")
            self._pressed = False
        else:
            self.config(bg="#6f6f6f")
            for id_ in self._texts:
                self.itemconfigure(id_, fill="#9f9f9f")
            self._pressed = False

    def create_dynamictext(self, x, y, text="", font=None, anchor=None):
        id_ = self.create_text(x, y, text=text, font=font, anchor=anchor)
        if self._hovered:
            self.itemconfigure(id_, fill="#afafaf")
        elif self._pressed:
            self.itemconfigure(id_, fill="#7f7f7f")
        else:
            self.itemconfigure(id_, fill="#9f9f9f")
        self._texts.append(id_)

    def delete(self, tag_or_id):
        if tag_or_id in self._texts:
            self._texts.remove(tag_or_id)


class Uploader(object):
    def __init__(self, conn, path, progressbar, *, on_complete=lambda: None,
                 on_error: Callable[[Exception], Any] = lambda exc: None):
        self.conn: socket = conn
        self._fd = open(path, "rb")
        self._thread: Optional[Thread] = None

        self.progressbar: Progressbar = progressbar

        try:
            self.totalBytesSent = 0
            self.totalFileSize = os.path.getsize(path)
        except Exception as e:
            on_error(e)

        # print(self.totalFileSize)

        self.on_error = on_error
        self.on_complete = on_complete

        self.done = False

    def upload(self):
        try:
            a = self.totalFileSize.to_bytes(16, "big", signed=False)
            self.conn.send(a)

            # print(self.totalFileSize, a)

            block = self._fd.read(1024)
            self.conn.sendall(block)
            self.totalBytesSent += 1024

            # while block:
            #     del block
            #     block = self._fd.read(1024)
            #     self.conn.sendall(block)
            #     self.totalBytesSent += 1024

            print(f"Expected to send: {self.totalFileSize} Bytes")

            while block:
                del block
                if self.totalFileSize - self.totalBytesSent >= 1024:
                    # print(f"Sending: {1024} Bytes")
                    block = self._fd.read(1024)
                    self.conn.sendall(block)
                    # if self.totalBytesSent == self.totalFileSize:
                    #     break
                    self.totalBytesSent += 1024
                else:
                    s = self.totalFileSize % 1024
                    block = self._fd.read(s)
                    self.conn.sendall(block)
                    # if self.totalBytesSent == self.totalFileSize:
                    #     break
                    self.totalBytesSent += s
                    break

            self._fd.close()
        except Exception as e:
            self.on_error(e)
        print("Sent:", self.totalBytesSent, "Bytes")
        self.done = True
        self.on_complete()

    def start(self):
        self._thread = Thread(target=lambda: self.upload())
        self._thread.start()


class Downloader(object):
    def __init__(self, conn, path, progressbar, *, on_complete=lambda: None,
                 on_error: Callable[[Exception], Any] = lambda exc: None):
        self.conn: socket = conn

        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            self._fd = open(path, "ab+")
        except Exception as e:
            self.done = True
            on_error(e)
        self._thread: Optional[Thread] = None

        self.progressbar: Progressbar = progressbar

        try:
            a = conn.recv(16)

            self.totalBytesRecieved = 0
            self.totalFileSize = int.from_bytes(a, "big", signed=False)
        except Exception as e:
            on_error(e)

        # print(self.totalFileSize)
        # print(a)

        self.on_error = on_error
        self.on_complete = on_complete

        self.done = False

    # noinspection PyUnreachableCode
    def download(self):
        print(f"Expecting to recieve: {self.totalFileSize} Bytes")
        try:
            while True:
                # if self.totalFileSize - self.totalBytesRecieved >= 1024:
                block = self.conn.recv(1024)
                # self._fd.seek(self.totalBytesRecieved)
                self._fd.write(block)
                self.totalBytesRecieved += len(block)
                # print(f"Recieved {len(block)} Bytes | Total {self.totalBytesRecieved}")
                # self.totalBytesRecieved = os.path.getsize(self._fd.name)
                if self.totalBytesRecieved == self.totalFileSize:
                    break
            self._fd.close()
            print("Recieved:", os.path.getsize(self._fd.name), "Bytes")
        except Exception as e:
            self.done = True
            self.on_error(e)
        self.done = True
        self.on_complete()

    def start(self):
        self._thread = Thread(target=lambda: self.download())
        self._thread.start()


class QCopyOverPC(Tk):
    def __init__(self):
        self.connection: Optional[Union[Server, Client]] = None

        self.selectWindow = Tk()
        self.theme(self.selectWindow)

        c_font_t = ("helvetica", 10)

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
            self.canv = self.sw.canv
            self.canv.config(bg="#4f4f4f")

            # self.frame.
            self.frame_sw = self.sw.scrollwindow
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

            self.openButton = QCanvasButton(self.frame, command=self.openfile, height=64)
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
        try:
            while True:
                for uploader in self.connection.uploaders().copy():
                    uploader: Uploader
                    if not uploader.done:
                        try:
                            uploader.progressbar.config(maximum=uploader.totalFileSize, value=uploader.totalBytesSent)
                        except TclError:
                            uploader.done = True
                    if uploader.done:
                        self.connection.uploaders().remove(uploader)
                for downloader in self.connection.downloaders().copy():
                    downloader: Downloader
                    if not downloader.done:
                        try:
                            downloader.progressbar.config(maximum=downloader.totalFileSize, value=downloader.totalBytesRecieved)
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
        progressbar.destroy()

        if (description is not None) and (new_description is not None):
            canvas.itemconfig(description, text=new_description)

    @staticmethod
    def on_error(canvas, progressbar, description, exc: Exception):
        progressbar.destroy()

        canvas.itemconfig(description, text=f"ERROR:\n    {exc.__class__.__name__}: {exc.__str__()}")

    def add_upload_item(self, name, title, description, path):
        titlefont = ("Helvetica", 20)
        infofont = ("Helvetica", 10)

        self.frames.append(Frame(self.frame_sw, height=150, width=790, bg="#6f6f6f"))
        self.canvass.append(
            Canvas(self.frames[-1], height=150, width=790, bg="#6f6f6f", highlightthickness=0))
        self.canvass[-1].pack(fill="x")
        canv: Canvas = self.canvass[-1]
        self._id[self.canvass[-1]] = {}
        self._id[self.canvass[-1]]["Title"] = self.canvass[-1].create_text(
            10, 10, text=title, fill="#a7a7a7", anchor="nw", font=titlefont)
        self._id[self.canvass[-1]]["Filename"] = self.canvass[-1].create_text(
            10, 40, text=name, fill="#a7a7a7", anchor="nw", font=infofont)
        desc = self._id[self.canvass[-1]]["Description"] = self.canvass[-1].create_text(
            10, 60, text=description, fill="#a7a7a7", anchor="nw", font=infofont)
        self.canvass[-1].create_rectangle(-1, 0, 790, 149, outline="#676767")
        self.canvass[-1].bind("<ButtonRelease-1>",
                              lambda event, c=self.canvass[-1]: self._on_canv_lclick(c))
        # self.canvass[-1].bind("<Double-Button-1>", lambda event, n_=name: self.open_direct(n_))
        self.canvass[-1].bind("<Motion>", lambda event, c=self.canvass[-1]: self._on_canv_motion(c))
        self.canvass[-1].bind("<Leave>", lambda event, c=self.canvass[-1]: self._on_canv_leave(c))

        progressbar = Progressbar(self.frames[-1], maximum=10, value=0)
        canv.create_window(10, 110, window=progressbar, width=770, height=30, anchor="nw")
        self.names[self.canvass[-1]] = name
        # self.index[self.canvass[-1]] = i
        self.frames[-1].pack(fill="x")

        self.connection.upload(
            path, progressbar,
            on_complete=lambda _canv=canv: self.on_complete(
                _canv, None, progressbar, desc, "Upload complete!"),
            on_error=lambda exc, _canv=canv: self.on_error(_canv, progressbar, desc, exc))

    def add_download_item(self, name, title, description, path):
        titlefont = ("Helvetica", 20)
        infofont = ("Helvetica", 10)

        self.frames.append(Frame(self.frame_sw, height=150, width=790, bg="#6f6f6f"))
        canv = Canvas(self.frames[-1], height=150, width=790, bg="#6f6f6f", highlightthickness=0)
        self.canvass.append(canv)
        self.canvass[-1].pack(fill="x")
        # canv: Canvas = self.canvass[-1]
        self._id[self.canvass[-1]] = {}
        self._id[self.canvass[-1]]["Title"] = self.canvass[-1].create_text(
            10, 10, text=title, fill="#a7a7a7", anchor="nw", font=titlefont)
        self._id[self.canvass[-1]]["Filename"] = self.canvass[-1].create_text(
            10, 40, text=name, fill="#a7a7a7", anchor="nw", font=infofont)
        desc = self._id[self.canvass[-1]]["Description"] = self.canvass[-1].create_text(
            10, 60, text=description, fill="#a7a7a7", anchor="nw", font=infofont)
        self.canvass[-1].create_rectangle(-1, 0, 790, 149, outline="#676767")
        self.canvass[-1].bind("<ButtonRelease-1>",
                              lambda event, c=self.canvass[-1]: self._on_canv_lclick(c))
        # self.canvass[-1].bind("<Double-Button-1>", lambda event, n_=name: self.open_direct(n_))
        self.canvass[-1].bind("<Motion>", lambda event, c=self.canvass[-1]: self._on_canv_motion(c))
        self.canvass[-1].bind("<Leave>", lambda event, c=self.canvass[-1]: self._on_canv_leave(c))

        progressbar = Progressbar(self.frames[-1], maximum=10, value=0)
        canv.create_window(10, 110, window=progressbar, width=770, height=30, anchor="nw")
        self.names[self.canvass[-1]] = name
        # self.index[self.canvass[-1]] = i
        self.frames[-1].pack(fill="x")

        # print(path)
        self.connection.download(
            path, progressbar,
            on_complete=lambda _canv=canv: self.on_complete(
                _canv, None, progressbar, desc, "Download complete!"),
            on_error=lambda exc, _canv=canv: self.on_error(_canv, progressbar, desc, exc))

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

    def savefile(self, filename, data):
        # files = [('Unknown FileType', f'*{os.path.splitext(filename)[-1]}')]
        # f = filedialog.asksaveasfile(filetypes=files, mode='wb', defaultextension=os.path.splitext(filename)[-1])

        if len(self.connection.uploaders()) >= 1:
            return
        if len(self.connection.downloaders()) >= 1:
            return

        f = filedialog.askdirectory(title=f"Save File: {filename}", mustexist=True)
        path = os.path.join(f, filename)

        # with open(path, "wb+") as file:
        #     file.write(data)
        self.add_download_item(data["filename"], "Download", "Downloading File (in queue)", path)
        # print(f)
        # f.write(data)

    def openfile(self):
        if self.connection is None:
            return

        if len(self.connection.uploaders()) >= 1:
            return
        if len(self.connection.downloaders()) >= 1:
            return

        files = [('Any File', f'*.*')]
        f = filedialog.askopenfile("rb", title="Open File", filetypes=files)
        if f is None:
            return

        f.seek(0)
        # f.read()

        if self.connection:
            data_send = {"type": "file", "filename": os.path.split(str(f.name))[-1]}
            self.connection.queue(data_send)
            # uploader = self.connection.upload(a.name)
            # uploader.totalBytesSent
            self.add_upload_item(data_send["filename"], "Upload", "Uploading File (in queue)", f.name)
            # print(a)
            del data_send

    def do(self, data):
        # print(data)
        if data["type"] == "file":
            self.savefile(data["filename"], data)

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
