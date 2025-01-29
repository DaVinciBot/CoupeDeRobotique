from config_loader import CONFIG

import time
from old_logger.logger import Logger, LogLevels
import logger as new_logger
import logging

use_old_logger = False

if use_old_logger:
    logger = Logger(
        identifier="Logger",
        decorator_level=LogLevels.DEBUG,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
        print_log=True,
        write_to_file=False
    )
else:
    logger = logging.getLogger("Logger")
    logger.setLevel(logging.DEBUG)
    formatter = new_logger.Formatter(
        identifier="Logger",
        identifier_max_width=12,
        level_max_width=8,
        colors=new_logger.colors.ClassicColors()
    )

    file_handler = logging.FileHandler("logs.txt")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

start_time = time.time()

for i in range(1000):
    if use_old_logger:
        logger.log(f"msg DEBUG: {i}", LogLevels.DEBUG)
        logger.log(f"msg INFO: {i}", LogLevels.INFO)
        logger.log(f"msg WARNING: {i}", LogLevels.WARNING)
        logger.log(f"msg CRITICAL: {i}", LogLevels.CRITICAL)
        logger.log(f"msg FATAL: {i}", LogLevels.FATAL)
    else:
        logger.debug(f"msg DEBUG: {i}")
        logger.info(f"msg INFO: {i}")
        logger.warning(f"msg WARNING: {i}")
        logger.critical(f"msg CRITICAL: {i}")
        logger.fatal(f"msg FATAL: {i}")

print(f"Execution duration: {time.time() - start_time}")

"""
Tests results:

decorator_level=LogLevels.DEBUG,
print_log_level=LogLevels.DEBUG,
file_log_level=LogLevels.DEBUG,
print_log=False,
write_to_file=False
-> 1.8772363662719727s

decorator_level=LogLevels.DEBUG,
print_log_level=LogLevels.DEBUG,
file_log_level=LogLevels.DEBUG,
print_log=True,
write_to_file=True
-> 2.247742176055908s

decorator_level=LogLevels.DEBUG,
print_log_level=LogLevels.DEBUG,
file_log_level=LogLevels.DEBUG,
print_log=False,
write_to_file=True
-> 2.077554702758789s

decorator_level=LogLevels.DEBUG,
print_log_level=LogLevels.DEBUG,
file_log_level=LogLevels.DEBUG,
print_log=True,
write_to_file=False
-> 2.193124771118164

decorator_level=LogLevels.DEBUG,
print_log_level=LogLevels.FATAL,
file_log_level=LogLevels.DEBUG,
print_log=True,
write_to_file=False
-> 2.191094398498535
"""
