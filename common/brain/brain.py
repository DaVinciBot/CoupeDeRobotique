from logger import Logger, LogLevels

class Brain:
    def __init__(self, logger: Logger) -> None:
        self.logger = logger 
    
    async def logical(self):
        pass
    
    async def routine(self):
        self.logger.log(f"Brain [{self.__class__.__name__}] started", LogLevels.INFO)
        while True:
            try:
                await self.logical()
            except Exception as error:
                self.logger.log(f"Brain [{self.__class__.__name__}] error: {error}", LogLevels.ERROR)
