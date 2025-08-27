"""Placeholder utilities for controlling an addressable LED strip."""

# from rpi_ws281x import PixelStrip, Color, RGBW
# from old_logger.log_tools import LogLevels
# from old.old_logger.logger import Logger
# import math

# LogColors = {
#     LogLevels.DEBUG: Color(0, 0, 255),
#     LogLevels.INFO: Color(0, 0, 255),
#     LogLevels.WARNING: Color(250, 250, 0),
#     LogLevels.ERROR: Color(255, 0, 0),
#     LogLevels.CRITICAL: Color(255, 0, 255),
#     LogLevels.FATAL: Color(255, 0, 0),
# }


# class Colors:
#     RED = Color(255, 0, 0)
#     GREEN = Color(0, 255, 0)
#     BLUE = Color(0, 0, 255)
#     WHITE = Color(255, 255, 255)
#     BLACK = Color(0, 0, 0)
#     YELLOW = Color(255, 255, 0)
#     CYAN = Color(0, 255, 255)
#     MAGENTA = Color(255, 0, 255)
#     ORANGE = Color(255, 165, 0)
#     PINK = Color(255, 192, 203)
#     PURPLE = Color(128, 0, 128)
#     BROWN = Color(165, 42, 42)


# class LEDStrip:
#     def __init__(self, num_leds, pin, frequency, brightness, led_indexes):
#         self._strip = PixelStrip(
#             num=num_leds, pin=pin, freq_hz=frequency, brightness=brightness
#         )
#         self._strip.begin()
#         self.led_indexes = led_indexes

#         self.log_size = 7
#         self.is_ready_index = 7
#         self.jeck_index = 8
#         self.team_index = 9

#         self.log_history = [Colors.BLACK for _ in list(range(self.log_size))]

#         self.set_color(Color(0, 0, 0))
#         self.set_is_ready(False)
#         self.set_jack(False)
#         self.set_pillars(Color(20, 20, 20))

#     def set_color(
#         self, color: RGBW | list[RGBW] | tuple[int], index: list | int | None = None
#     ):
#         if isinstance(color, tuple):
#             color = Color(*color)
#         if index is None and isinstance(color, RGBW):
#             for i in range(self._strip.numPixels()):
#                 self._strip.setPixelColor(i, color)
#         if isinstance(index, int) and isinstance(color, RGBW):
#             self._strip.setPixelColor(index, color)
#         if (
#             isinstance(index, list)
#             and isinstance(color, list)
#             and len(index) == len(color)
#         ):
#             for i, j in enumerate(index):
#                 self._strip.setPixelColor(j, color[i])
#         if isinstance(index, list) and isinstance(color, RGBW):
#             for i in index:
#                 self._strip.setPixelColor(i, color)
#         self._strip.show()

#     def set_color_range(self, start, end, color):
#         for i in range(start, end):
#             self._strip.setPixelColor(i, color)
#         self._strip.show()

#     def set_color_single(self, index, color):
#         self._strip.setPixelColor(index, color)
#         self._strip.show()

#     def clear(self):
#         self.set_color(Color(0, 0, 0))

#     def set_pillars(
#         self, color: RGBW | list[RGBW] | tuple[int], index: list | int | None = None
#     ):
#         self.set_color(color, self.get_pillars_indexes(index))

#     def get_pillars_indexes(self, index: int | list[int] | None) -> list[int]:
#         indexes: list[int] = []
#         pillar_names = [
#             "inside_front_right",
#             "inside_back_right",
#             "inside_back_left",
#             "inside_front_left",
#         ]

#         if index is None:
#             index = [
#                 i
#                 for i in range(
#                     max(
#                         [
#                             len(self.led_indexes[pillar_name])
#                             for pillar_name in pillar_names
#                         ]
#                     )
#                 )
#             ]

#         if isinstance(index, list):
#             for i in index:
#                 for pillar_name in pillar_names:
#                     if i < len(self.led_indexes[pillar_name]):
#                         indexes.append(self.led_indexes[pillar_name][i])

#         else:  # Case int
#             for pillar_name in [
#                 "inside_front_right",
#                 "inside_back_right",
#                 "inside_back_left",
#                 "inside_front_left",
#             ]:
#                 if index < len(self.led_indexes[pillar_name]):
#                     indexes.append(self.led_indexes[pillar_name][index])

#         return indexes

#     def log(self, log_level: LogLevels):
#         self.log_history.insert(0, LogColors[log_level])
#         del self.log_history[-1]
#         self.set_pillars(self.log_history, list(range(7)))

#     def set_is_ready(self, state=True):
#         self.set_pillars(
#             Colors.GREEN if state else Colors.RED,
#             self.is_ready_index,
#         )

#     def set_jack(self, state):
#         self.set_pillars(Colors.GREEN if state else Colors.RED, self.jeck_index)

#     def set_team(self, team):
#         # print(f"Set team to {team}")
#         self.set_pillars(Colors.YELLOW if team == "y" else Colors.BLUE, self.team_index)

#     def set_lidar_info(
#         self,
#         triggered: bool = False,
#         angle: float | None = None,
#         max_angle: float = 2 * math.pi,
#         min_angle: float = 0.0,
#     ):
#         """Lights up led in given direction (proportionally)

#         Args:
#             direction (float): angle in rads
#             max_angle (float): max possible angle
#             min_angle (float): min possible angle (default 0.0)
#         """

#         if angle is None:
#             self.set_color(
#                 Colors.ORANGE if triggered else Colors.BLACK,
#                 self.led_indexes["lidar"],
#             )
#         else:
#             angle %= math.tau
#             min_angle %= math.tau
#             max_angle %= math.tau
#             index = int(
#                 ((angle - min_angle) % math.tau)
#                 / ((max_angle - min_angle) % math.tau)
#                 * len(self.led_indexes["lidar"])
#             )

#             if index == len(self.led_indexes):
#                 index -= 1  # Edge case

#             self.set_color(
#                 Colors.YELLOW if triggered else Colors.WHITE,
#                 self.led_indexes["lidar"][:index]
#                 + self.led_indexes["lidar"][index + 1 :],
#             )
#             self.set_color(Colors.RED, self.led_indexes["lidar"][index])

#     def set_score(self, score: int):
#         self.set_color(
#             Colors.BLACK,
#             self.led_indexes["score"]["tens"] + self.led_indexes["score"]["units"],
#         )
#         tens = score // 10
#         units = score % 10
#         if tens >= 10:
#             tens = 9
#             units = 9

#         self.set_color(Colors.WHITE, self.led_indexes["score"]["tens"][tens])
#         self.set_color(Colors.WHITE, self.led_indexes["score"]["units"][units])
