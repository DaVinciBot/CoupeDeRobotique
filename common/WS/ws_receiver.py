import asyncio
import json

import aiohttp

from WS.ws_message import WSmsg


class WSreceiver:
    """
    This class is used to receive messages from the server.
    It has a routine which listen every incoming message from its associated route.
    It stores them a queue or just save the last state.
    * It only manipulates WSmsg objects (not WSMessage).
    * It is completely dedicated to work with the determined message format.
    """

    def __init__(self, use_queue: bool = False, keep_memory: bool = False) -> None:
        self.use_queue = use_queue
        self.keep_memory = keep_memory

        self.queue = asyncio.Queue()
        self.last_state = WSmsg()  # Set a default WSmsg object as default value

    async def routine(self, msg: aiohttp.WSMessage) -> None:
        """
        Coroutine to read received messages and add them in queues (one for each task).
        """
        msg = WSmsg.from_aiohttp_message(msg)

        if self.use_queue:
            await self.queue.put(msg)
        self.last_state = msg
        # print(f"New message {msg}")

    async def get(self, skip_queue: bool = False, wait_msg: bool = False) -> WSmsg:
        """
        Get state received. This method allows to skip_queue (get directly the last received state) / to wait_msg
        if the queue is empty, it will wait a new message and return it / to keep_memory if this option is True,
        this methode will save the last_state and return it on ask. If it's False, when a value is get, it will be deleted
        (next value is Empty WSmsg).
        :param skip_queue:
        :param wait_msg:
        :return:
        """
        if self.use_queue:
            if wait_msg:
                return await self.queue.get()
            elif not self.queue.empty():
                return await self.queue.get()

        if self.keep_memory:
            return self.last_state

        state = self.last_state
        self.last_state = WSmsg()
        return state

    def get_queue_size(self) -> int:
        """
        Get the size of the queue. Return 0 if the queue is not used.
        :return:
        """
        if self.use_queue:
            return self.queue.qsize()
        return 0
