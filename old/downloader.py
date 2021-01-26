import os
import shutil
from abc import ABC, abstractmethod
from socket import socket
from threading import Thread
from tkinter.ttk import Progressbar
from typing import Callable, Optional, BinaryIO
from uuid import UUID

from advUtils.network import PacketSystem
from old.gui import DownloadItem, CanvasItem
from lib import FileSize


class PreDownloader(ABC):
    def __init__(self):
        self.path: str
        self.progressbar: Progressbar

        self.onError: Callable[[Exception], None]
        self.onComplete: Callable[[], None]
        self.canvasItem: CanvasItem

    @abstractmethod
    def get_downloader(self, is_server: bool, pak: PacketSystem):
        pass


class Downloader(ABC):
    # noinspection PyTypeChecker
    def __init__(self):
        self.message: str = ""
        self.conn: PacketSystem = None
        self._fd: Optional[BinaryIO] = None
        self._thread: Optional[Thread] = None
        self.canvasItem: DownloadItem = None
        self.onError: Callable[[Exception], None] = None
        self.onComplete: Callable[[], None] = None
        self.progressbar: Progressbar = None

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def start(self):
        pass


class PreFileDownloader(PreDownloader):
    """
    Pre-downloader, initializes the download and when queued the #get_downloader(self, pak: PacketSystem) method will be called.
    @author: Quinten Jungblut
    """
    def __init__(self, conn: socket, path: str, progressbar: Progressbar, *, canvas_item: DownloadItem, on_complete: Callable[[], None] = lambda: None, on_error: Callable[[Exception], None] = lambda exc: None):
        super().__init__()
        self.path: str = path
        self.progressbar: Progressbar = progressbar

        self.onError = on_error
        self.onComplete = on_complete
        self.canvasItem: DownloadItem = canvas_item
        self.conn: socket = conn

    def get_downloader(self, is_server: bool, pak: PacketSystem) -> 'FileDownloader':
        """
        Returns a downloader.

        @param is_server:
        @param pak: the packet-system.
        @return: the downloader.
        @author: Quinten Jungblut
        """
        a = FileDownloader(is_server, pak, self.path, self.progressbar, on_complete=self.onComplete, on_error=self.onError, canvas_item=self.canvasItem)
        a.start()
        return a


class FileDownloader(Downloader):
    """
    Downloader, downloads a file.
    @author: Quinten Jungblut
    """
    def __init__(self, is_server: bool, pak: PacketSystem, path: str, progressbar: Progressbar, *, canvas_item: DownloadItem, on_complete: Callable[[], None] = lambda: None, on_error: Callable[[Exception], None] = lambda exc: None):
        super().__init__()
        self.conn: PacketSystem = pak
        self.isServer = is_server

        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            self._fd = open(path, "ab+")
            self._thread: Optional[Thread] = None

            self.onError = on_error
            self.onComplete = on_complete
            self.canvasItem = canvas_item

            self.progressbar: Progressbar = progressbar

            try:
                uuid = self.conn.recv()
                if isinstance(uuid, UUID):
                    uuid: UUID
                    self.uuid: UUID = uuid

                size = self.conn.recv()
                if isinstance(size, int):
                    size: int
                    self.fileSize: int = size

                self.bytesReceived = 0
            except Exception as e:
                self.done = True
                self.onError(e)

            self.done = False

        except Exception as e:
            self.done = True
            on_error(e)

    # noinspection PyUnreachableCode
    def download(self):
        """
        Download
        @author: Quinten Jungblut
        """
        print(f"Expecting to receive: {self.fileSize} Bytes")
        try:
            while True:
                receive_block = self.conn.recv()
                if receive_block["type"] == "data":
                    t_data = receive_block["data"]
                    block = t_data["data"]

                    self._fd.write(block)
                    self.bytesReceived += t_data["size"]
                    self.message = f"Downloaded: {FileSize.get_string(self.bytesReceived)}\n" \
                                   f"File size: {FileSize.get_string(self.fileSize)}"
                    if t_data["last-block"]:
                        break
                    self.message = f"Downloaded: {FileSize.get_string(self.bytesReceived)}\n" \
                                   f"File size: {FileSize.get_string(self.fileSize)}"
            self._fd.close()
            print("Received:", os.path.getsize(self._fd.name), "Bytes")

            self.done = True
            self.onComplete()
        except Exception as e:
            self.done = True
            try:
                self.conn.send({"type": "error", "error": {"exception": e}})
            except ConnectionError:
                pass
            self.onError(e)

    def start(self):
        """
        Starts a download.
        @author: Quinten Jungblut
        """
        self._thread = Thread(target=lambda: self.download())
        self._thread.start()


class PreFolderDownloader(PreDownloader):
    """
    Pre-downloader, initializes the download and when queued the #get_downloader(self, pak: PacketSystem) method will be called.
    @author: Quinten Jungblut
    """
    def __init__(self, conn: socket, path: str, progressbar: Progressbar, *, canvas_item: DownloadItem, on_complete: Callable[[], None] = lambda: None, on_error: Callable[[Exception], None] = lambda exc: None):
        super().__init__()

        self.path: str = path
        self.progressbar: Progressbar = progressbar

        self.onError = on_error
        self.onComplete = on_complete
        self.canvasItem: DownloadItem = canvas_item
        self.conn: socket = conn

    def get_downloader(self, is_server: bool, pak: PacketSystem) -> 'FolderDownloader':
        """
        Returns a downloader.

        @param is_server:
        @param pak: the packet-system.
        @return: the downloader.
        @author: Quinten Jungblut
        """
        a = FolderDownloader(is_server, pak, self.path, self.progressbar, on_complete=self.onComplete, on_error=self.onError, canvas_item=self.canvasItem)
        a.start()
        return a


class FolderDownloader(Downloader):
    """
    Downloader, downloads a file.
    @author: Quinten Jungblut
    """
    def __init__(self, is_server: bool, pak: PacketSystem, path: str, progressbar: Progressbar, *, canvas_item: DownloadItem, on_complete: Callable[[], None] = lambda: None, on_error: Callable[[Exception], None] = lambda exc: None):
        super().__init__()
        self._fd: Optional[BinaryIO] = None
        self.conn: PacketSystem = pak
        self.isServer = is_server

        try:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
            self._thread: Optional[Thread] = None

            self.onError = on_error
            self.onComplete = on_complete
            self.canvasItem = canvas_item

            self.progressbar: Progressbar = progressbar

            try:
                uuid = self.conn.recv()
                if isinstance(uuid, UUID):
                    uuid: UUID
                    self.uuid: UUID = uuid

                size = self.conn.recv()
                if isinstance(size, int):
                    size: int
                    self.fileSize: int = size

                self.bytesReceived = 0
            except Exception as e:
                self.done = True
                self.onError(e)

            self.done = False
            self.path: str = path

        except Exception as e:
            self.done = True
            on_error(e)

    # noinspection PyUnreachableCode
    def download(self):
        """
        Download
        @author: Quinten Jungblut
        """
        print(f"Expecting to receive: {self.fileSize} Bytes")
        try:
            while True:
                receive_block = self.conn.recv()
                if receive_block["type"] == "create_file":
                    rel_path = receive_block["rel-path"]
                    self._fd = open(os.path.join(self.path, rel_path), "ab+")
                if receive_block["type"] == "create_folder":
                    rel_path = receive_block["rel-path"]
                    os.makedirs(self.path, rel_path)
                    continue
                elif receive_block["type"] == "end":
                    break
                while True:
                    receive_block = self.conn.recv()
                    if receive_block["type"] == "data-rel-path":
                        t_data = receive_block["data"]
                        # rel_path = receive_block["rel-path"]
                        block = t_data["data"]
                        self._fd.write(block)
                        self.bytesReceived += t_data["size"]
                        if t_data["last-block"]:
                            self.message = f"Downloaded: {FileSize.get_string(self.bytesReceived)}\n" \
                                           f"File size: {FileSize.get_string(self.fileSize)}"
                            break
                    self.message = f"Downloaded: {FileSize.get_string(self.bytesReceived)}\n" \
                                   f"File size: {FileSize.get_string(self.fileSize)}"
                self._fd.close()
            print("Received:", os.path.getsize(self._fd.name), "Bytes")

            self.done = True
            self.onComplete()
        except Exception as e:
            self.done = True
            try:
                self.conn.send({"type": "error", "error": {"exception": e}})
            except ConnectionError:
                pass
            self.onError(e)

    def start(self):
        """
        Starts a download.
        @author: Quinten Jungblut
        """
        self._thread = Thread(target=lambda: self.download())
        self._thread.start()
