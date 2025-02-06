# ====== Code Summary ======
# This script defines a `LogAnalyser` class that reads execution logs from a specified file,
# extracts function execution times using regular expressions, and plots them using Matplotlib.
# The script supports filtering execution times for specific function names and reports
# average execution times.

# ====== Imports ======
# Standard library imports
import re

# Third-party library imports
import matplotlib.pyplot as plt


class LogAnalyser:
    """
    A class to analyze execution times of functions from a log file.

    Attributes:
        log_file_path (str): Path to the log file containing execution records.
    """

    def __init__(self, log_file_path: str):
        """
        Initializes the LogAnalyser with the given log file path.

        Args:
            log_file_path (str): Path to the log file.
        """
        self.log_file_path = log_file_path

    def analyse_time_tracker(self, func_names: str | list[str] | None = None):
        """
        Analyzes execution times for specified functions and generates a plot.

        Args:
            func_names (str | list[str] | None, optional): Function name(s) to filter.
                - If a string is provided, only that function is analyzed.
                - If a list of strings is provided, only those functions are analyzed.
                - If None, all functions are analyzed.
        """
        if isinstance(func_names, str):
            func_names = [func_names]
        elif func_names is None:
            func_names = [".*"]  # Match all functions

        # Regular expression pattern to capture function execution times
        pattern = (
            r"\[\S+\] "  # Match any section enclosed in brackets, e.g., [INFO]
            r"([\w\.]+)"  # Capture function name, allowing for dots in names
            r"\(.*?\)"  # Capture potential arguments without being greedy
            r" executed in "  # Fixed phrase
            r"(\d+\.\d+)"  # Capture execution time in decimal format
            r"s"
        )

        times = {}

        try:
            # Open and read the log file
            with open(self.log_file_path, "r") as log_file:
                log_lines = log_file.readlines()

            # Extract execution times for each matching function
            for line in log_lines:
                match = re.search(pattern, line)
                if match:
                    function_name, execution_time = match.group(1), match.group(2)
                    if any(re.fullmatch(fn, function_name) for fn in func_names):
                        if function_name not in times:
                            times[function_name] = [execution_time]
                        else:
                            times[function_name].append(execution_time)

            if not times:
                print("No matching execution times found in the log file.")
                return

            # Plot the execution times
            plt.figure(figsize=(10, 6))

            for func_name, time_list in times.items():
                time_list = [float(time) * 1000 for time in time_list]  # Convert seconds to milliseconds
                average_time = sum(time_list) / len(time_list)
                plt.plot(
                    time_list,
                    label=f"{func_name} (Avg: {average_time:.6f} ms)",
                    marker="o",
                )

            # Configure plot labels and title
            plt.xlabel("Execution Count")
            plt.ylabel("Time (ms)")
            plt.title("Function Execution Times")
            plt.legend()
            plt.grid(True)
            plt.show()

        except FileNotFoundError:
            print(f"Error: The file '{self.log_file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")