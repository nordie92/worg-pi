import threading
from time import sleep
import configparser
import adafruit_dht
import board
from util import Util

class SensorTask:
    def __init__(self):
        self.thread_event = threading.Event()
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.interval = self.config['default'].getint('sensor_task_interval')
        self.dht_device = adafruit_dht.DHT11(Util.get_pin('D4'))
    
    def read_dht11(self):
        temperature_c = self.dht_device.temperature
        humidity = self.dht_device.humidity
        return temperature_c, humidity
    
    def backgroundTask(self):
        while self.thread_event.is_set():
            try:
                print(self.read_dht11())
                print('sensor task running...')
            except Exception as e:
                print(e)
                print('sensor task error...')
            finally:
                sleep(self.interval)

    def start_task(self):
        self.thread_event.set()
        threading.Thread(target=self.backgroundTask).start()