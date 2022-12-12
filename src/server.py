import asyncio
import logging

from server.probe_handler import ProbeHandler
from server.provider_handler import ProviderHandler

logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.DEBUG)
    probe_handler = ProbeHandler()
    provider_handler = ProviderHandler()
    probe_server = await asyncio.start_server(probe_handler.handle, '::', 5555)
    provider_server = await asyncio.start_server(provider_handler.handle, '::', 6666)
    await asyncio.gather(
            probe_server.serve_forever(),
            provider_server.serve_forever()
        )

if __name__ == "__main__":
    asyncio.run(main())