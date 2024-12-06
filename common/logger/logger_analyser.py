from matplotlib import pyplot as plt
import re

class LogerAnalyser():
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path

    def analyse_func_time_tracker(self,func_name):
        """
        Given a log file, calculate the average time taken by the specified function and plot the times.
        
        :param log_file_path: Path to the log file containing execution times.
        """
        pattern = rf"Function `{func_name}` executed in (\d+\.\d+) seconds"
        
        times = []

        try:
            with open(self.log_file_path, 'r') as log_file:
                log_lines = log_file.readlines()
            
            for line in log_lines:
                match = re.search(pattern, line)
                if match:
                    times.append(float(match.group(1)))

            if not times:
                print("No execution times found in the log file.")
                return

            average_time = sum(times) / len(times)
            print(f"Average time taken: {average_time:.6f} seconds")

            plt.figure(figsize=(10, 6))
            plt.plot(times, label="Execution Time", marker='o', color='b')

            plt.axhline(y=average_time, color='r', linestyle='--', label=f'Average Time ({average_time:.6f} s)')

            # Labels and title
            plt.xlabel("Execution Count")
            plt.ylabel("Time (seconds)")
            plt.title(f"Execution Times of {func_name}")
            plt.legend()

            # Show the plot
            plt.grid(True)
            plt.show()

        except FileNotFoundError:
            print(f"Error: The file '{self.log_file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")