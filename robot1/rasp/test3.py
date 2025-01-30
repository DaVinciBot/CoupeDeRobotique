from config_loader import CONFIG
from remote import PS5Remote, RemoteSimulator
from logger import Logger, LogLevels

remote = PS5Remote(Logger(identifier="remote"))
simulator = RemoteSimulator(remote)
simulator.run()
