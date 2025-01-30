from matplotlib import pyplot as plt
from old_logger.constants import TRACK_TIME_STR
import re


class LogAnalyser:
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path

    def analyse_time_tracker(self, func_names: str | list[str] | None = None):
        """
        Given a log file, calculate the average time taken by the specified function and plot the times.

        :param log_file_path: Path to the log file containing execution times.
        """
        if isinstance(func_names, str):
            func_names = [func_names]
        elif func_names is None:
            func_names = [".*"]

        pattern = (
            re.escape(TRACK_TIME_STR)
            .replace(r"\{func_name\}", r"(" + "|".join(func_names) + r")")
            .replace(r"\{elapsed_time\}", r"(\d+\.\d+)")
        )

        times = {}

        try:
            with open(self.log_file_path, "r") as log_file:
                log_lines = log_file.readlines()

            for line in log_lines:
                match = re.search(pattern, line)
                if match:
                    if match.group(1) not in times:
                        times[match.group(1)] = [match.group(2)]
                    else:
                        times[match.group(1)].append(match.group(2))

            if not times:
                print("No execution times found in the log file.")
                return

            plt.figure(figsize=(10, 6))

            for func_name, time_list in times.items():
                time_list = list(
                    map(lambda x: float(x) * 1000, time_list)
                )  # Convert to ms
                average_time = sum(time_list) / len(time_list)
                plt.plot(
                    time_list,
                    label=f"{func_name} (Avg: {average_time:.6f} ms)",
                    marker="o",
                )

            plt.xlabel("Execution Count")
            plt.ylabel("Time (ms)")
            plt.title("Execution Times")
            plt.legend()

            plt.grid(True)
            plt.show()

        except FileNotFoundError:
            print(f"Error: The file '{self.log_file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
