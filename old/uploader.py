import os
from abc import ABC, abstractmethod
from threading import Thread
from tkinter.ttk import Progressbar
from typing import Callable, Any, Optional, BinaryIO
from uuid import uuid3, NAMESPACE_X500, UUID

from advUtils.network import PacketSystem
from old.gui import UploadItem, CanvasItem
from lib import FileSize


class PreUploader(ABC):
    def __init__(self):
        self.path: str
        self.progressbar: Progressbar

        self.onError: Callable[[Exception], None]
        self.onComplete: Callable[[], None]
        self.canvasItem: CanvasItem

    @abstractmethod
    def get_uploader(self, pak: PacketSystem):
        pass


class Uploader(ABC):
    # noinspection PyTypeChecker
    def __init__(self):
        self.message: str = ""
        self.conn: PacketSystem = None
        self._fd: Optional[BinaryIO] = None
        self._thread: Optional[Thread] = None
        self.canvasItem: UploadItem = None
        self.onError: Callable[[Exception], None] = None
        self.onComplete: Callable[[], None] = None
        self.progressbar: Progressbar = None

    @abstractmethod
    def upload(self):
        pass

    @abstractmethod
    def start(self):
        pass


class PreFileUploader(PreUploader):
    """
    Pre-uploader, initializes the upload and when queued the #get_uploader(self, pak: PacketSystem) method will be called.
    @author: Quinten Jungblut
    """

    def __init__(self, path: str, progressbar: Progressbar, *, canvas_item: UploadItem, on_complete=lambda: None, on_error=lambda exc: None):
        super().__init__()
        self.path = path
        self.progressbar = progressbar

        self.onError = on_error
        self.onComplete = on_complete
        self.canvasItem = canvas_item

    def get_uploader(self, pak: PacketSystem) -> 'FileUploader':
        """
        Returns a uploader.

        @param pak:
        @author: Quinten Jungblut
        @return: the uploader
        """
        a = FileUploader(pak, self.path, self.progressbar, on_complete=self.onComplete, on_error=self.onError, canvas_item=self.canvasItem)
        a.start()
        return a


class FileUploader(Uploader):
    """
    Uploader, uploads a file.
    @author: Quinten Jungblut
    """

    def __init__(self, pak: PacketSystem, path, progressbar, *, canvas_item: UploadItem, on_complete=lambda: None, on_error: Callable[[Exception], Any] = lambda exc: None):
        super().__init__()
        self.pak: PacketSystem = pak
        self._fd = open(path, "rb")
        self._thread: Optional[Thread] = None
        self.uuid = uuid3(NAMESPACE_X500, path)

        self.progressbar: Progressbar = progressbar

        try:
            self.bytesSent = 0
            self.fileSize = os.path.getsize(path)
        except Exception as e:
            on_error(e)

        # print(self.totalFileSize)

        self.onError = on_error
        self.onComplete = on_complete
        self.canvasItem = canvas_item

        self.done = False

    def upload(self):
        """
        Upload
        @author: Quinten Jungblut
        """
        try:
            # a = self.totalFileSize.to_bytes(16, "big", signed=False)
            self.pak.send(self.uuid)
            self.pak.send(self.fileSize)

            print(f"Expected to send: {self.fileSize} Bytes")

            while True:
                self.message = f"Uploaded: {FileSize.get_string(self.bytesSent)}\n" \
                               f"File size: {FileSize.get_string(self.fileSize)}\n"
                self.send_block(32767)
                self.message = f"Uploaded: {FileSize.get_string(self.bytesSent)}\n" \
                               f"File size: {FileSize.get_string(self.fileSize)}\n"
                if self.done:
                    break
                self.message = f"Uploaded: {FileSize.get_string(self.bytesSent)}\n" \
                               f"File size: {FileSize.get_string(self.fileSize)}\n"
            self._fd.close()
        except Exception as e:
            self.done = True
            self.onError(e)
            return
        print("Sent:", self.bytesSent, "Bytes")
        self.done = True
        self.onComplete()

    def start(self):
        """
        Start upload.
        @author: Quinten Jungblut
        """

        # Disabled thread upload because upload conflicts caused by having 1 port used.
        # self.upload()

        self._thread = Thread(target=lambda: self.upload())
        self._thread.start()

    def send_block(self, size):
        """
        Sends a block.

        @param size: size to send.
        @author: Quinten Jungblut
        """
        self.message = f"Uploaded: {FileSize.get_string(self.bytesSent)}\n" \
                       f"File size: {FileSize.get_string(self.fileSize)}\n"
        data: bytes = self._fd.read(size)
        size1 = len(data)
        if size1 < size:
            self.done = True
        self.pak.send({"type": "data", "data": {"size": size1, "data": data, "last-block": self.done}})
        self.bytesSent += size1
        self.message = f"Uploaded: {FileSize.get_string(self.bytesSent)}\n" \
                       f"File size: {FileSize.get_string(self.fileSize)}\n"


class PreFolderUploader(PreUploader):
    """
    Pre-uploader, initializes the upload and when queued the #get_uploader(self, pak: PacketSystem) method will be called.
    @author: Quinten Jungblut
    """

    def __init__(self, path, progressbar, *, canvas_item: UploadItem, on_complete=lambda: None, on_error=lambda exc: None):
        super().__init__()
        self.path = path
        self.progressbar = progressbar

        self.onError = on_error
        self.onComplete = on_complete
        self.canvasItem = canvas_item

    def get_uploader(self, pak: PacketSystem) -> 'FolderUploader':
        """
        Returns a uploader.

        @param pak:
        @author: Quinten Jungblut
        @return: the uploader
        """
        a = FolderUploader(pak, self.path, self.progressbar, on_complete=self.onComplete, on_error=self.onError, canvas_item=self.canvasItem)
        a.start()
        return a


class FolderUploader(Uploader):
    """
    Uploader, uploads a file.
    @author: Quinten Jungblut
    """

    def __init__(self, pak: PacketSystem, path, progressbar, *, canvas_item: UploadItem, on_complete=lambda: None, on_error: Callable[[Exception], Any] = lambda exc: None):
        super().__init__()
        self.doneFile = False
        self._fd: Optional[BinaryIO] = None
        self.pak: PacketSystem = pak
        self._thread: Optional[Thread] = None
        self.uuid: UUID = uuid3(NAMESPACE_X500, path)

        self.progressbar: Progressbar = progressbar

        try:
            self.bytesSent = 0
        except Exception as e:
            on_error(e)

        # print(self.totalFileSize)

        self.onError: Callable[[Exception], None] = on_error
        self.onComplete: Callable[[], None] = on_complete
        self.canvasItem: UploadItem = canvas_item
        self.path: str = path
        self.currentPath: str = path
        self.currentFile: Optional[str] = None

        self.totalSize = 0

        self.totalSize = self.calculate_size()
        self.pak.sendall(self.totalSize)

        self.done = False

    def upload(self):
        """
        Upload
        @author: Quinten Jungblut
        """

        # a = self.totalFileSize.to_bytes(16, "big", signed=False)
        self.pak.sendall(self.uuid)

        self.upload_folder(self.path)

        self.pak.sendall({"type": "end"})

        self.done = True
        self.onComplete()

    def upload_folder(self, path: str):
        try:
            print(f"Expected to send: {self.totalSize} Bytes")

            self.currentPath = path

            for item in os.listdir(path):
                i_path = os.path.join(path, item)

                if os.path.isdir(i_path):
                    self.pak.sendall({"type": "create-folder", "rel-path": os.path.relpath(i_path, self.path).replace(os.sep, "/")})
                    self.upload_folder(i_path)
                elif os.path.isfile(i_path):
                    self.upload_file(item)
        except Exception as e:
            self.onError(e)
            self.done = True
        print("Sent:", self.bytesSent, "Bytes")

    def upload_file(self, filename: str):
        try:
            self.currentFile = path = os.path.join(self.currentPath, filename)
            rel_path: str = os.path.relpath(path, self.path).replace(os.sep, "/")
            norm_path: str = os.path.realpath(os.path.abspath(path))
            file_size: int = os.path.getsize(norm_path)
            self.pak.sendall({"type": "create-file", "rel-path": rel_path, "size": file_size})

            self._fd = open(path, "rb")

            while True:
                self.send_block(65536)
                self.message = f"Uploaded: {FileSize.get_string(self.bytesSent)}\n" \
                               f"Total size: {FileSize.get_string(self.totalSize)}\n" \
                               f"Current path: {path}"
                if self.doneFile:
                    break
        except Exception as e:
            self.onError(e)
            try:
                self.pak.sendall({"type": "error", "error": {"exception": e}})
            except ConnectionError:
                pass
            except PermissionError:
                pass

    def start(self):
        """
        Start upload.
        @author: Quinten Jungblut
        """

        self.upload()

    def send_block(self, size: int):
        """
        Sends a block.

        @param size: size to send.
        @author: Quinten Jungblut
        """

        data: bytes = self._fd.read(size)
        size1 = len(data)
        if size1 < size:
            self.done = True
        self.pak.sendall({"type": "data-rel-path", "rel-path": os.path.relpath(self.currentFile, self.path), "data": {"size": size1, "data": data, "last-block": self.done}})
        self.bytesSent += size1

    def calculate_size(self) -> int:
        def file(path):
            return os.path.getsize(path)

        def folder(path, total_size):
            folder_size = 0
            for item in os.listdir(path):
                self.message = f"Calculating file size...\n" \
                               f"Path: {path}\n" \
                               f"Current size: {FileSize.get_string(folder_size + total_size)}"
                i_path = os.path.join(path, item)
                if os.path.isdir(i_path):
                    folder_size += folder(i_path, folder_size + total_size)
                elif os.path.isfile(i_path):
                    folder_size += file(i_path)
                self.message = f"Calculating file size...\n" \
                               f"Path: {path}\n" \
                               f"Current size: {FileSize.get_string(folder_size + total_size)}"
            return folder_size

        return folder(self.path, 0)
