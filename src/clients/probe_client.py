import logging
import socket

from typing import Optional

from clients.client import Client
from clients.streams import TcpStream, ApduStream
from tunnelTypes.connect import (AuthStatus, ConnectRequest, ConnectResponse, Imsi, Iccid,
                             ConnectStatus, Token)

logger = logging.getLogger(__name__)

class ProbeClient(Client):
    def __init__(self, identifier: int, token: Token, host, port):
        super().__init__(identifier, token, host, port)

    def connect(self, sim_id: Imsi | Iccid) -> Optional[ApduStream]:
        logger.debug("Opening connection.")
        stream = TcpStream(socket.create_connection((self.host, self.port)))

        try:
            apdu_stream = self._connect(stream, sim_id)
        except:
            stream.close()
            return None

        if apdu_stream == None:
            stream.close()

        return apdu_stream

    def _connect(self, stream: TcpStream, sim_id: Imsi | Iccid) -> Optional[ApduStream]:
        auth_status = self._authenticate(stream)

        if auth_status != AuthStatus.Success:
            logger.info("Authorisation failed!")
            return None

        logger.debug(f"Sending connection request ({sim_id})")
        stream.write_all(ConnectRequest(sim_id).encode())

        logger.debug("Waiting for answer to connection request message.")
        conn_res = ConnectResponse.decode(stream.read_exactly(ConnectResponse.LENGTH))

        if conn_res == None:
            logger.warn("Received malformed message during connection.")
            return None

        if conn_res.status != ConnectStatus.Success:
            logger.info(f"Requesting SIM {sim_id} failed!")
            return None

        return ApduStream(stream)