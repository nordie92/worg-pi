import threading
from time import sleep
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

interval = config['default'].getint('sensor_task_interval')

thread_event = threading.Event()

def backgroundTask():
    while thread_event.is_set():
        print('sensor task running...')
        sleep(interval)

def start_task():
    thread_event.set()
    backgroundTask()