from abc import ABC, abstractmethod
from enum import Enum
from tkinter import Canvas, Frame
from tkinter.ttk import Progressbar
from typing import Callable, List, Union, TextIO, BinaryIO, Dict
import globals as _g
import tkinter as _tk
import pathlib as _p
import json as _json


class ColorType(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"
    NORMAL = "normal"


class ThemeEntry(object):
    def __init__(self, data: dict):
        self._data = data
        
    def get(self, key: str) -> object:
        return self._data[key]
    
    def get_int(self, key: str) -> int:
        value = self._data[key]
        if isinstance(value, int):
            return value
        else:
            return 0

    def get_float(self, key: str) -> float:
        value = self._data[key]
        if isinstance(value, float):
            return value
        else:
            return 0.0

    def get_str(self, key: str) -> str:
        value = self._data[key]
        if isinstance(value, str):
            return value
        else:
            return ""

    def get_list(self, key: str) -> list:
        value = self._data[key]
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return list(value)
        else:
            return []

    def get_tuple(self, key: str) -> tuple:
        value = self._data[key]
        if isinstance(value, list):
            return tuple(value)
        elif isinstance(value, tuple):
            return value
        elif isinstance(value, set):
            return tuple(value)
        else:
            return ()

    def get_set(self, key: str) -> set:
        value = self._data[key]
        if isinstance(value, list):
            return set(value)
        elif isinstance(value, tuple):
            return set(value)
        elif isinstance(value, set):
            return value
        else:
            return set()


class Theme(object):
    def __init__(self):
        self.entries: Dict[str, ThemeEntry] = {}
        
    def load(self, file: Union[_p.Path, str, TextIO, BinaryIO]):
        if isinstance(file, _p.Path):
            data = _json.loads(file.read_text("utf-8"))
        elif isinstance(file, str):
            fd = open(file, "r", encoding="utf-8")
            data = _json.loads(fd.read())
            fd.close()
        elif isinstance(file, TextIO):
            data = _json.loads(file.read())
        elif isinstance(file, BinaryIO):
            data = _json.loads(file.read())
        else:
            raise TypeError(f"File is not of a valid type.")
        
        if isinstance(data, dict):
            self.__load0(data)
        else:
            raise TypeError(f"Theme data is not a list.")

    def __load0(self, data: dict):
        entries: Dict[str, ThemeEntry] = {}
        
        for key, value in data.items():
            if isinstance(key, str):
                if isinstance(value, dict):
                    entries[key] = ThemeEntry(value)
                else:
                    raise TypeError(f"Entry mapping has invalid value type.")
            else:
                raise TypeError(f"Entry mapping has invalid key type.")
            
        self.entries = entries
        
    def get(self, key: str) -> ThemeEntry:
        return self.entries[key]


class Widget(ABC):
    def __init__(self, parent: 'Widget'):
        self.theme: Theme = parent.theme
        self.parent: Widget = parent
        self._tk_widget: _tk.Misc = self.create()
        self.configure(self._tk_widget)
            
    @abstractmethod
    def create(self) -> _tk.Misc:
        pass
    
    @abstractmethod
    def configure(self, widget: '_tk.Misc') -> '_tk.Misc':
        pass


class Window(Widget):
    def __init__(self, parent: 'Window'):
        super().__init__(parent)
        
        self.parent: Window
        self._tk_widget: _tk.Tk

    def create(self) -> _tk.Tk:
        return _tk.Tk()
    
    def configure(self, widget: '_tk.Tk') -> _tk.Tk:
        widget.mainloop()
        return widget
        
    def close(self):
        self._tk_widget.destroy()


class Panel(Widget):
    def create(self) -> _tk.Frame:
        return _tk.Frame(self.parent._tk_widget, background=self.theme.get("panel"))

    def configure(self, widget: '_tk.Frame') -> '_tk.Frame':
        pass


class FileView(Widget):
    def configure(self, widget: '_tk.Misc') -> '_tk.Misc':
        pass

    def create(self) -> _tk.Misc:
        pass

    def __init__(self, parent: 'Widget'):
        super().__init__(parent)


class CanvasItem(Canvas, ABC):
    def __init__(self, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, **kw)

    # noinspection SpellCheckingInspection
    def _on_canvas_leave(self, hover_canvas):
        """
        Canvas-leave event handler.

        :param hover_canvas:
        :return:
        """

        # if self._hoverCanvasOld is not None:
        #     if self.selectedCanvas != self._hoverCanvasOld:
        #         self._hoverCanvasOld.config(bg="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Title"], fill="#bfbfbf")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Filename"], fill="#bfbfbf")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Description"], fill="#bfbfbf")
        #         # for subid in self._id[self._hoverCanvasOld]["Infos"]:
        #         #     self._hoverCanvasOld.itemconfig(subid, fill="#bfbfbf")
        #     else:
        #         self._hoverCanvasOld.config(bg="#4f4f4f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Title"], fill="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Filename"], fill="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Description"], fill="#7f7f7f")
        #         # for subid in self._id[self._hoverCanvasOld]["Infos"]:
        #         #     self._hoverCanvasOld.itemconfig(subid, fill="#00bfbf")
        # self._hoverCanvasOld = None

    # noinspection SpellCheckingInspection
    def _on_canvas_motion(self, hover_canvas):
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
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Title"], fill="#bfbfbf")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Filename"], fill="#bfbfbf")
        #         self._hoverCanvasOld.itemconfig(self._id[self._hoverCanvasOld]["Description"], fill="#bfbfbf")
        #         # for subid in self._id[self._hoverCanvasOld]["Infos"]:
        #         #     self._hoverCanvasOld.itemconfig(subid, fill="#939393")
        #     else:
        #         self._hoverCanvasOld.config(bg="#4f4f4f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Title"], fill="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Filename"], fill="#7f7f7f")
        #         self._hoverCanvasOld.itemconfig(self._id[hover_canvas]["Description"], fill="#7f7f7f")
        #         # for subid in self._id[self._hoverCanvasOld]["Infos"]:
        #         #     self._hoverCanvasOld.itemconfig(subid, fill="#00bfbf")
        # self._hoverCanvasOld = hover_canvas
        #
        # if hover_canvas != self.selectedCanvas:
        #     hover_canvas.config(bg="#bfbfbf")
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

    # noinspection SpellCheckingInspection
    def _on_canvas_l_click(self, c: Canvas):
        """
        Canvas-left-click event handler.

        :param c:
        :return:
        """

        # if self.oldSelected is not None:
        #     self.oldSelected.config(bg="#7f7f7f")
        #     self.oldSelected.itemconfig(self._id[self.oldSelected]["Title"], fill="#bfbfbf")
        #     self.oldSelected.itemconfig(self._id[self.oldSelected]["Filename"], fill="#bfbfbf")
        #     self.oldSelected.itemconfig(self._id[self.oldSelected]["Description"], fill="#bfbfbf")
        #     # for subid in self._id[self.oldSelected]["Infos"]:
        #     #     self.oldSelected.itemconfig(subid, fill="#939393")
        # self.oldSelected = c
        #
        # c.config(bg="#00bfbf")
        # c.itemconfig(self._id[c]["Title"], fill="#ffffff")
        # c.itemconfig(self._id[c]["Filename"], fill="#bfbfbf")
        # c.itemconfig(self._id[c]["Description"], fill="#bfbfbf")
        # # for subid in self._id[c]["Infos"]:
        # #     c.itemconfig(subid, fill="#00dada")
        #
        # self.selectedCanvas = c

    @abstractmethod
    def set_color(self, color: ColorType) -> None:
        """
        @author: Quinten Jungblut
        """
        pass


class DownloadItem(CanvasItem, ABC):
    def __init__(self, qcopyoverpc, name="<UNKNOWN>", description="<UNKNOWN>", **kw):
        if qcopyoverpc is None:
            raise ValueError("qcopyoverpc must be specified.")
        title = "Download"

        super().__init__(qcopyoverpc.frames[-1], **kw)
        title_font = ("Helvetica", 20)
        info_font = ("Helvetica", 10)

        # noinspection PyProtectedMember
        self._id = qcopyoverpc._id
        self.canvass = qcopyoverpc.canvass
        self.names = qcopyoverpc.names
        self.frames = qcopyoverpc.frames

        self.onError: Callable[[Exception], None] = lambda exc: None
        self.onComplete: Callable[[], None] = lambda: None

        self.canvass.append(self)
        # canv: Canvas = self.canvass[-1]
        self._id[self.canvass[-1]] = {}
        self.title = self._id[self.canvass[-1]]["Title"] = self.canvass[-1].create_text(
            10, 10, text=title, fill="#bfbfbf", anchor="nw", font=title_font)
        self.name = self._id[self.canvass[-1]]["Filename"] = self.canvass[-1].create_text(
            10, 40, text=name, fill="#bfbfbf", anchor="nw", font=info_font)
        self.desc = self._id[self.canvass[-1]]["Description"] = self.canvass[-1].create_text(
            10, 60, text=description, fill="#bfbfbf", anchor="nw", font=info_font)
        self.canvass[-1].create_rectangle(-1, 0, 790, 149, outline="#676767")
        self.canvass[-1].bind("<ButtonRelease-1>",
                              lambda event, c=self.canvass[-1]: self._on_canvas_l_click(c))
        # self.canvass[-1].bind("<Double-Button-1>", lambda event, n_=name: self.open_direct(n_))
        self.canvass[-1].bind("<Motion>", lambda event, c=self.canvass[-1]: self._on_canvas_motion(c))
        self.canvass[-1].bind("<Leave>", lambda event, c=self.canvass[-1]: self._on_canvas_leave(c))

        self.progressbar = Progressbar(self.frames[-1], maximum=10, value=0)

        self.create_window(10, 110, window=self.progressbar, width=770, height=30, anchor="nw")
        self.names[self.canvass[-1]] = name

    def set_description(self, text: str):
        self.itemconfigure(self.desc, text=text)

    def set_title(self, text: str):
        self.itemconfigure(self.title, text=text)

    def update_progress(self, value: int):
        self.progressbar.config(value=value)

    def set_file_size(self, size: int):
        self.progressbar.config(maximum=size)

    def set_color(self, color: ColorType) -> None:
        """
        @param color: the color 
        """

        if color == ColorType.ERROR:
            background = "#7f0000"
            text = "#bf0000"
        elif color == ColorType.WARNING:
            background = "#7f3f00"
            text = "#bf5f00"
        elif color == ColorType.INFO:
            background = "#00007f"
            text = "#0000bf"
        elif color == ColorType.SUCCESS:
            background = "#007f00"
            text = "#00bf00"
        else:
            background = "7f7f7f"
            text = "#bfbfbf"

        self.configure(bg=background)
        self.itemconfig(self.title, fill=text)
        self.itemconfig(self.desc, fill=text)
        self.itemconfig(self.name, fill=text)


class UploadItem(CanvasItem):
    def __init__(self, qcopyoverpc, name="<UNKNOWN>", description="<UNKNOWN>", **kw):
        if qcopyoverpc is None:
            raise ValueError("qcopyoverpc must be specified.")
        title = "Upload"

        super().__init__(qcopyoverpc.frames[-1], **kw)
        title_font = ("Helvetica", 20)
        info_font = ("Helvetica", 10)

        # noinspection PyProtectedMember
        self._id = qcopyoverpc._id
        self.canvass = qcopyoverpc.canvass
        self.names = qcopyoverpc.names
        self.frames = qcopyoverpc.frames

        self.onError: Callable[[Exception], None] = lambda exc: None
        self.onComplete: Callable[[], None] = lambda: None

        self.canvass.append(self)
        # canv: Canvas = self.canvass[-1]
        self._id[self.canvass[-1]] = {}
        self.title = self._id[self.canvass[-1]]["Title"] = self.canvass[-1].create_text(
            10, 10, text=title, fill="#bfbfbf", anchor="nw", font=title_font)
        self.name = self._id[self.canvass[-1]]["Filename"] = self.canvass[-1].create_text(
            10, 40, text=name, fill="#bfbfbf", anchor="nw", font=info_font)
        self.desc = self._id[self.canvass[-1]]["Description"] = self.canvass[-1].create_text(
            10, 60, text=description, fill="#bfbfbf", anchor="nw", font=info_font)
        self.canvass[-1].create_rectangle(-1, 0, 790, 149, outline="#676767")
        self.canvass[-1].bind("<ButtonRelease-1>",
                              lambda event, c=self.canvass[-1]: self._on_canvas_l_click(c))
        # self.canvass[-1].bind("<Double-Button-1>", lambda event, n_=name: self.open_direct(n_))
        self.canvass[-1].bind("<Motion>", lambda event, c=self.canvass[-1]: self._on_canvas_motion(c))
        self.canvass[-1].bind("<Leave>", lambda event, c=self.canvass[-1]: self._on_canvas_leave(c))

        self.progressbar = Progressbar(self.frames[-1], maximum=10, value=0)

        self.create_window(10, 110, window=self.progressbar, width=770, height=30, anchor="nw")
        self.names[self.canvass[-1]] = name

    def set_description(self, text: str):
        self.itemconfigure(self.desc, text=text)

    def set_title(self, text: str):
        self.itemconfigure(self.title, text=text)

    def update_progress(self, value: int):
        self.progressbar.config(value=value)

    def set_file_size(self, size: int):
        self.progressbar.config(maximum=size)

    def set_color(self, color: ColorType) -> None:
        """
        @param color: the color
        """

        if color == ColorType.ERROR:
            background = "#7f0000"
            text = "#bf0000"
        elif color == ColorType.WARNING:
            background = "#7f3f00"
            text = "#bf5f00"
        elif color == ColorType.INFO:
            background = "#00007f"
            text = "#0000bf"
        elif color == ColorType.SUCCESS:
            background = "#007f00"
            text = "#00bf00"
        else:
            background = "7f7f7f"
            text = "#bfbfbf"

        self.configure(bg=background)
        self.itemconfig(self.title, fill=text)
        self.itemconfig(self.desc, fill=text)
        self.itemconfig(self.name, fill=text)


class ErrorItem(CanvasItem):
    def __init__(self, qforgeutils, name="<UNKNOWN>", description="<UNKNOWN>", **kw):
        if qforgeutils is None:
            raise ValueError("qforgeutils must be specified.")
        title = "Error"

        super().__init__(qforgeutils.frames[-1], **kw)
        titlefont = ("Helvetica", 20)
        infofont = ("Helvetica", 10)

        # noinspection PyProtectedMember
        self._id = qforgeutils._id
        self.canvass = qforgeutils.canvass
        self.names = qforgeutils.names
        self.frames = qforgeutils.frames

        description = name + "\n" + description

        self.canvass.append(self)
        # canv: Canvas = self.canvass[-1]
        self._id[self.canvass[-1]] = {}
        self.title = self._id[self.canvass[-1]]["Title"] = self.canvass[-1].create_text(
            10, 10, text=title, fill="#bf0000", anchor="nw", font=titlefont)
        self.desc = self._id[self.canvass[-1]]["Description"] = self.canvass[-1].create_text(
            10, 60, text=description, fill="#bf0000", anchor="nw", font=infofont)
        self.canvass[-1].create_rectangle(-1, 0, 790, 149, outline="#6f0000")
        self.canvass[-1].bind("<ButtonRelease-1>",
                              lambda event, c=self.canvass[-1]: self._on_canvas_l_click(c))
        # self.canvass[-1].bind("<Double-Button-1>", lambda event, n_=name: self.open_direct(n_))
        self.canvass[-1].bind("<Motion>", lambda event, c=self.canvass[-1]: self._on_canvas_motion(c))
        self.canvass[-1].bind("<Leave>", lambda event, c=self.canvass[-1]: self._on_canvas_leave(c))
        self.names[self.canvass[-1]] = name

        self.set_color(ColorType.ERROR)

    def set_description(self, text: str):
        self.itemconfigure(self.desc, text=text)

    def set_title(self, text: str):
        self.itemconfigure(self.title, text=text)

    def set_color(self, color: ColorType) -> None:
        """
        @param color: the color
        """

        if color == ColorType.ERROR:
            background = "#7f0000"
            text = "#bf0000"
        elif color == ColorType.WARNING:
            background = "#7f3f00"
            text = "#bf5f00"
        elif color == ColorType.INFO:
            background = "#00007f"
            text = "#0000bf"
        elif color == ColorType.SUCCESS:
            background = "#007f00"
            text = "#00bf00"
        else:
            background = "7f7f7f"
            text = "#bfbfbf"

        self.configure(bg=background)
        self.itemconfig(self.title, fill=text)
        self.itemconfig(self.desc, fill=text)


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
            self.config(bg="#00bfbf")
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

    # noinspection PyUnusedLocal
    def _on_release(self, evt):
        if self._hovered:
            self.config(bg="#00bfbf")
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
            self.itemconfigure(id_, fill="#bfbfbf")
        elif self._pressed:
            self.itemconfigure(id_, fill="#7f7f7f")
        else:
            self.itemconfigure(id_, fill="#9f9f9f")
        self._texts.append(id_)

    def delete(self, tag_or_id):
        if tag_or_id in self._texts:
            self._texts.remove(tag_or_id)


class ScrolledWindow(Frame):
    """
    1. Master widget gets scrollbars and a canvas. Scrollbars are connected to the canvas scroll-region.
    2. self.scroll_window is created and inserted into canvas

    Usage Guideline:
    =================
      Assign any widgets as children of <ScrolledWindow instance>.scroll_window
      to get them inserted into canvas

      __init__(self, parent, canvas_w = 400, canvas_h = 400, *args, **kwargs)

    Docstring:
    ===========
    @param parent: master of scrolled window.
    @param canvas_w: width of canvas
    @param canvas_h: height of canvas
    """

    def __init__(self, parent, canvas_w=400, canvas_h=400, expand=False, fill=None, height=None, width=None, *args,
                 scroll_command=lambda: None, scrollbar_bg=None, scrollbar_fg="darkgray", **kwargs):
        """
        Parent =

        @param parent: master of scrolled window.
        @param canvas_w: width of canvas
        @param canvas_h: height of canvas
        @param expand: expand the widget.
        @param fill: fill the widget.
        @param height: height of the widget.
        @param width: width of the widget.
        @param args: alternative arguments for the widget.
        @param scroll_command: callback for scrolling.
        @param scrollbar_bg: scrollbar background color.
        @param scrollbar_fg: scrollbar foreground color.
        @param kwargs: alternative keyword arguments for the widget.
        """
        super().__init__(parent, height=canvas_h, width=canvas_w, *args, **kwargs)

        self.parent = parent
        self.scrollCommand = scroll_command

        # creating a scrollbars

        if width is None:
            __width = 0
        else:
            __width = width

        if height is None:
            __height = 0
        else:
            __height = width

        self.canvas = Canvas(self.parent, bg='#FFFFFF', width=canvas_w, height=canvas_h,
                             scrollregion=(0, 0, __width, __height), highlightthickness=0)

        self.vbar = CustomVerticalScrollbar(self.parent, width=10, command=self.canvas.yview, bg=scrollbar_bg, fg=scrollbar_fg, bd=0)
        self.canvas.configure(yscrollcommand=self.vbar.set)

        self.vbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=fill, expand=expand)

        # creating a frame to insert to canvas
        self.scroll_window = Frame(self.parent, height=height, width=width)

        self.scroll_window2 = self.canvas.create_window(0, 0, window=self.scroll_window, anchor='nw', height=height,
                                                        width=width)

        self.canvas.config(
            yscrollcommand=self.vbar.set,
            scrollregion=(0, 0, canvas_h, canvas_w))

        self.scroll_window.bind('<Configure>', self._configure_window)
        self.scroll_window.bind('<Enter>', self._bound_to_mousewheel)
        self.scroll_window.bind('<Leave>', self._unbound_to_mousewheel)

        return

    # noinspection PyUnusedLocal
    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    # noinspection PyUnusedLocal
    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # noinspection PyUnusedLocal
    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scroll_window.winfo_reqwidth(), self.scroll_window.winfo_reqheight() + 1)
        self.canvas.config(scrollregion='0 0 %s %s' % size)


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
        if "fg" in kw:
            del kw["fg"]
        if "bd" in kw:
            bd = kw.pop("bd")
        if "border" in kw:
            bd = kw.pop("border")
        if "highlightthickness" in kw:
            hlt = kw.pop("highlightthickness")
        Canvas.__init__(self, parent, **kw, highlightthickness=hlt, border=bd, bd=bd)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"

        self._x0: int = 0
        self._x1: int = 0
        self._y0: int = 0
        self._y1: int = 0

        self.pressed_x: int = -1

        # coordinates are irrelevant; they will be recomputed in the 'set' method\
        self.old_y = 0
        self._id = self.create_rectangle(0, 0, 1, 1, fill=kwargs["fg"], outline=kwargs["fg"], tags=("thumb",))
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def configure(self, cnf=None, **kwargs):
        command = kwargs.pop("command", None)
        self.command = command if command is not None else self.command
        kw = kwargs.copy()
        if "fg" in kw:
            del kw["fg"]
        super().configure(**kw, highlightthickness=0, border=0, bd=0)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"
        self.itemconfig(self._id, fill=kwargs["fg"], outline=kwargs["fg"])

    def config(self, cnf=None, **kwargs):
        self.configure(cnf, **kwargs)

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
    def on_release(self, event):
        self.unbind("<Motion>")

    def on_click(self, event):
        x = event.x / self.winfo_width()
        x0 = self._x0
        x1 = self._x1
        a = x + ((x1 - x0) / -(self.winfo_width() * 2))
        self.command("moveto", a)


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
        if "fg" in kw:
            del kw["fg"]
        if "bd" in kw:
            bd = kw.pop("bd")
        if "border" in kw:
            bd = kw.pop("border")
        if "highlightthickness" in kw:
            hlt = kw.pop("highlightthickness")
        Canvas.__init__(self, parent, **kw, highlightthickness=hlt, border=bd, bd=bd)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"

        self._x0: int = 0
        self._x1: int = 0
        self._y0: int = 0
        self._y1: int = 0
        self.pressed_y: int = 0

        # coordinates are irrelevant; they will be recomputed in the 'set' method
        self.old_y = 0
        self._id = self.create_rectangle(0, 0, 1, 1, fill=kwargs["fg"], outline=kwargs["fg"], tags=("thumb",))
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def configure(self, cnf=None, **kwargs):
        command = kwargs.pop("command", None)
        self.command = command if command is not None else self.command
        kw = kwargs.copy()
        if "fg" in kw:
            del kw["fg"]
        super().configure(**kw, highlightthickness=0, border=0, bd=0)
        if "fg" not in kwargs.keys():
            kwargs["fg"] = "darkgray"
        self.itemconfig(self._id, fill=kwargs["fg"], outline=kwargs["fg"])

    def config(self, cnf=None, **kwargs):
        self.configure(cnf, **kwargs)

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
    def on_release(self, event):
        self.unbind("<Motion>")

    def on_click(self, event):
        y = event.y / self.winfo_height()
        y0 = self._y0
        y1 = self._y1
        a = y + ((y1 - y0) / -(self.winfo_height() * 2))
        self.command("moveto", a)
