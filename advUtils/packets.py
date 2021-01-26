from abc import ABC
from socket import socket
from typing import Dict


class Packet(ABC):
    TYPES: Dict[int, 'Packet']

    def __init__(self, id_: int):
        if id_ in Packet.TYPES:
            raise ValueError(f"Duplicate packet type: {id_}")

    def send(self, conn: socket):

        conn.send()
