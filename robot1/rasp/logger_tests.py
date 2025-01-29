from config_loader import CONFIG

import time

from logger import (
    Logger, LogLevels,
    ClassicColors, DarkModeColors, NeonColors, PastelColors, CyberpunkColors,
    time_tracker, log
)

logger = Logger(
    identifier="Logger",
    decorator_log_level=LogLevels.DEBUG,
    print_log_level=LogLevels.DEBUG,
    file_log_level=LogLevels.DEBUG,
    print_log=True,
    write_to_file=True,
    colors=NeonColors
)


@time_tracker(param_logger="Logger")
def test(x=5):
    for i in range(1000):
        logger.debug(f"msg DEBUG: {i}")
        logger.info(f"msg INFO: {i}")
        logger.warning(f"msg WARNING: {i}")
        logger.critical(f"msg CRITICAL: {i}")
        logger.fatal(f"msg FATAL: {i}")


test()

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
