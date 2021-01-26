from pickle import UnpicklingError
from socket import socket
from threading import Thread
from time import sleep
from tkinter.ttk import Progressbar
from typing import List, Callable, Dict
from uuid import UUID, uuid3, NAMESPACE_X500

from old import __main__
from advUtils import network
from advUtils.network import PacketSystem
from old.downloader import PreFileDownloader, PreFolderDownloader, PreDownloader, Downloader
from old.gui import DownloadItem, UploadItem
from old.uploader import PreFileUploader, PreFolderUploader, PreUploader, Uploader


class Server(network.Server):
    """
    QCopyOverPC server.
    """

    def __init__(self, main: '__main__.QCopyOverPC'):
        super(Server, self).__init__(43393)
        self._upQueue: Dict[socket, List[object]] = {}
        self._downQueue: List[object] = []

        self.uploading: Dict[UUID, List[socket]] = {}

        self.main: '__main__.QCopyOverPC' = main
        self._uploaders: List[Uploader] = []
        self._downloaders: List[Downloader] = []

    def on_complete(self, conn: socket, path: str, complete: Callable[[], None]):
        """
        File-upload complete callback.

        @param conn: the socket connection.
        @param path: the filepath.
        @param complete: alternative upload-complete callback.
        @author: Quinten Jungblut
        """

        sockets: List[socket] = self.uploading.get(uuid3(NAMESPACE_X500, path))
        sockets.remove(conn)
        if len(sockets) == 0:
            complete()

    def up_queue(self, conn: socket, data: object):
        """
        Queue a upload to a single socket.

        @param conn:
        @param data:
        @author: Quinten Jungblut
        """

        self._upQueue[conn].append(data)

    def up_queue_all(self, data: object):
        """
        Queue a upload to all sockets.

        @param data: the data for the upload.
        @author: Quinten Jungblut
        """
        for conn in self.conn_array:
            self._upQueue[conn].append(data)

    def down_queue(self, data: object):
        """
        Queue a download.

        @param data: the data of the download request.
        @author: Quinten Jungblut
        """

        self._downQueue.append(data)

    def send(self, conn: socket, o: object):
        self.up_queue(conn, o)

    def sendall(self, o: object):
        self.up_queue_all(o)

    def upload_folder(self, path: str, progressbar: Progressbar, *, on_complete: Callable[[], None] = lambda: None, on_error: Callable[[Exception], None] = lambda exc: None, canvas_item: UploadItem):
        self.uploading[uuid3(NAMESPACE_X500, path)] = []
        for conn in self.conn_array:
            self.uploading[uuid3(NAMESPACE_X500, path)].append(conn)
            self.up_queue(conn, PreFolderUploader(path, progressbar, on_complete=lambda a_=conn, b_=path, c_=on_complete: self.on_complete(a_, b_, c_), on_error=on_error, canvas_item=canvas_item))

    def upload(self, path: str, progressbar: Progressbar, *, on_complete: Callable[[], None] = lambda: None, on_error: Callable[[Exception], None] = lambda exc: None, canvas_item: UploadItem):
        """
        Download a file to the socket.

        @param path: the path to the file to be uploaded.
        @param progressbar: the progressbar.
        @param on_complete: callable event for when upload completes.
        @param on_error: callable event for when an error occurs.
        @param canvas_item: the canvas item for displaying the upload progress.
        @author: Quinten Jungblut
        """

        self.uploading[uuid3(NAMESPACE_X500, path)] = []
        for conn in self.conn_array:
            self.uploading[uuid3(NAMESPACE_X500, path)].append(conn)
            self.up_queue(conn, PreFileUploader(path, progressbar, on_complete=lambda a_=conn, b_=path, c_=on_complete: self.on_complete(a_, b_, c_), on_error=on_error, canvas_item=canvas_item))

    def download_folder(self, conn: socket, path: str, progressbar: Progressbar, *, on_complete: Callable[[], None] = lambda: None, on_error: Callable[[Exception], None] = lambda exc: None, canvas_item: DownloadItem):
        """
        Download a file from socket.

        @param conn: the socket connection.
        @param path: the filepath.
        @param progressbar: the progressbar.
        @param on_complete: callable event for when download completes.
        @param on_error: callable event for when an error occurs.
        @param canvas_item: the canvas item for displaying the download progress.
        @author: Quinten Jungblut
        """

        self.down_queue(PreFolderDownloader(conn, path, progressbar, on_complete=on_complete, on_error=on_error, canvas_item=canvas_item))

    def download(self, conn: socket, path: str, progressbar: Progressbar, *, on_complete: Callable[[], None] = lambda: None, on_error: Callable[[Exception], None] = lambda exc: None, canvas_item: DownloadItem):
        """
        Download a file from socket.

        @param conn: the socket connection.
        @param path: the filepath.
        @param progressbar: the progressbar.
        @param on_complete: callable event for when download completes.
        @param on_error: callable event for when an error occurs.
        @param canvas_item: the canvas item for displaying the download progress.
        @author: Quinten Jungblut
        """

        self.down_queue(PreFileDownloader(conn, path, progressbar, on_complete=on_complete, on_error=on_error, canvas_item=canvas_item))

    def uploaders(self):
        """
        Returns uploaders

        @return: uploaders.
        @author: Quinten Jungblut
        """

        return self._uploaders

    def downloaders(self):
        """
        Returns downloaders

        @return: downloaders
        @author: Quinten Jungblut
        """

        return self._downloaders

    def receiver(self, conn: socket):
        """
        Receiver for server connections.

        @param conn: the socket connection.
        @author: Quinten Jungblut
        """

        pak = PacketSystem(conn)

        try:
            while True:
                sleep(0.1)
                # if not self._queue:
                #     continue
                if not self._downloaders:
                    received = pak.recv()
                    if received is not None:
                        self.main.do(conn, received)
                    if not self._downQueue:
                        continue
                    data = self._downQueue.pop(0)
                    if isinstance(data, PreDownloader):
                        self._downloaders.append(data.get_downloader(True, pak))
                        continue
        except OverflowError:
            Thread(target=lambda: self.receiver(conn)).start()
        except MemoryError:
            Thread(target=lambda: self.receiver(conn)).start()
        except UnpicklingError:
            Thread(target=lambda: self.receiver(conn)).start()
        except Exception as e:
            self.main.add_error_item(e.__class__.__name__, "Error occurred in receiver\n" + e.__str__())

    def runner(self, conn: socket, secret):
        """
        Socket connection runner.

        @param conn: the socket connection.
        @param secret: the encryption key.
        @author: Quinten Jungblut
        """

        self._upQueue[conn] = []
        Thread(target=lambda: self.sender(conn)).start()
        Thread(target=lambda: self.receiver(conn)).start()

    def sender(self, conn: socket):
        """
        Sender for server connections.

        @param conn: the socket connection.
        @author: Quinten Jungblut
        """

        pak = PacketSystem(conn)

        try:
            while True:
                sleep(0.1)
                if not self._upQueue[conn]:
                    continue
                data = self._upQueue[conn].pop(0)
                if isinstance(data, PreUploader):
                    self._uploaders.append(data.get_uploader(pak))
                    continue
                # print(data)
                if data:
                    pak.send(data)
        except Exception as e:
            self.main.add_error_item(e.__class__.__name__, f"Error occurred in sender: {e.__class__.__name__}\n" + e.__str__())
