import aiohttp
import json
import time


class WSmsg:
    """
    This class is used to manipulate message object based on the determined message format.
    {
        "sender": str,
        "msg": str,
        "data": any,
        "ts": int
    }
    """

    def __init__(self, sender: str = None, msg: str = None, data: any = None, ts: int = None) -> None:
        self.sender = sender
        self.msg = msg
        self.data = data
        self.ts = ts

    @classmethod
    def from_json(cls, msg: dict):
        """
        Convert a json to a message object.
        :param msg:
        :return:
        """
        return cls(
            sender=str(msg.get("sender")),
            msg=str(msg.get("msg")),
            data=msg.get("data"),
            ts=int(msg.get("ts"))
        )

    @classmethod
    def from_str(cls, msg: str):
        """
        Convert a string to a message object.
        :param msg:
        :return:
        """
        msg = json.loads(msg)
        return self.from_json(msg)

    @classmethod
    def from_aiohttp_message(cls, msg: aiohttp.WSMessage):
        """
        Convert aiohttp.WSMessage to a message object.
        :param msg:
        :return:
        """
        if msg.type == aiohttp.WSMsgType.TEXT:
            msg_json = msg.json()
            return cls(
                sender=msg_json.get("sender"),
                msg=msg_json.get("msg"),
                data=msg_json.get("data"),
                ts=msg_json.get("ts")
            )
        else:
            print(f"Unknown message type: {msg.type}")
            return cls()

    def to_str(self) -> str:
        """
        Convert the message to a string format.
        :return:
        """
        return json.dumps(self.to_json())

    def to_json(self) -> dict:
        """
        Convert the message to a json format.
        :return:
        """
        return {
            "sender": self.sender,
            "msg": self.msg,
            "data": self.data,
            "ts": self.ts
        }

    def prepare(self, str_format=True) -> str or dict:
        """
        Prepare the message to be sent, it could be str or json format (str by default).
        * It checks if the sender value is set.
        * It adds a timestamp if not set.
        * It raise warnings if msg or data are not set.
        :param str_format:
        :return:
        """
        if self.sender is None:
            raise ValueError("Sender value is None. PREPARATION FAILED.")

        if self.msg is None:
            print("Warning: msg is not set.")
        if self.data is None:
            print("Warning: data is not set.")

        if self.ts is None:
            self.ts = int(time.time())

        if str_format:
            return self.to_str()
        return self.to_json()

    def __str__(self) -> str:
        return f"(sender: {self.sender}, msg: {self.msg}, data: {self.data}, ts: {self.ts})"

    def __eq__(self, other: any) -> bool:
        if not isinstance(other, WSmsg):
            return NotImplemented
        return (
                self.sender == other.sender and
                self.msg == other.msg and
                self.data == other.data and
                self.ts == other.ts
        )
