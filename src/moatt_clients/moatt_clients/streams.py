import struct
import logging

from typing import Optional

from moatt_clients.errors import ProtocolError
from moatt_types.connect import ApduPacket, ApduOp

logger = logging.getLogger(__name__)

class RawStream:
    def __init__(self, socket):
        self.socket = socket
        self.buf = b""

    def getpeername(self):
        return self.socket.getpeername()

    def write_all(self, buf: bytes) -> None:
        self.socket.sendall(buf)

    def read_exactly(self, n: int) -> bytes:
        while True:
            if len(self.buf) >= n:
                b = self.buf[:n]
                self.buf = self.buf[n:]
                return b

            if not self._fill_buf():
                raise EOFError

    def read(self, n: int = -1) -> bytes:
        if len(self.buf) == 0:
            self._fill_buf()

        if n == -1:
            b = self.buf
            self.buf = b""
            return b
        else:
            b = self.buf[:n]
            self.buf = self.buf[n:]
            return b

    def _fill_buf(self) -> bool:
        b = self.socket.recv(1024)
        if len(b) == 0:
            return False
        else:
            self.buf += b
            return True

    def close(self) -> None:
        self.buf = b""
        self.socket.close()

class ApduStream:
    def __init__(self, stream: RawStream):
        self.stream = stream

    def getpeername(self):
        return self.stream.getpeername()

    def send_apdu(self, payload: bytes) -> None:
        self.send(ApduPacket(ApduOp.Apdu, payload))

    def send_reset(self) -> None:
        self.send(ApduPacket(ApduOp.Reset, b""))

    def send(self, packet: ApduPacket) -> None:
        self.stream.write_all(packet.encode())

    def recv(self) -> Optional[ApduPacket]:
        buf = self.stream.read(n=6)

        if len(buf) == 0:
            return None

        missing = ApduStream._bytes_missing(buf)
        while missing > 0:
            r = self.stream.read(n=missing)
            assert len(r) <= missing

            if len(r) == 0:
                raise EOFError

            buf += r
            missing = ApduStream._bytes_missing(buf)

        logger.debug(buf)
        p = ApduPacket.decode(buf)

        if p is None:
            raise ProtocolError("Received a malformed message.")

        return p

    def close(self) -> None:
        self.stream.close()

    @staticmethod
    def _bytes_missing(msg: bytes) -> int:
        if len(msg) < 6:
            return 6 - len(msg)

        plen, = struct.unpack("!I", msg[2:6])
        if len(msg) < 6 + plen:
            return (6 + plen) - len(msg)
        else:
            return 0
