from datetime import datetime


class Utils:
    @staticmethod
    def get_date() -> datetime:
        return datetime.now()

    @staticmethod
    def get_str_date(format: str = "%H:%M:%S") -> str:
        return datetime.now().strftime(format)

    @staticmethod
    def get_ts() -> float:
        return datetime.timestamp(datetime.now())
