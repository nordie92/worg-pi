import random
from threading import Thread
from time import sleep
import adafruit_dht
import digitalio
from util import UIConfigs, Util
import os
from datetime import datetime
from database import insert_sensor_data, insert_action

class Hardware:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Hardware, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self):
        self.sensor = None
        self.temperature = 0
        self.humidity = 0
        self.soil_moisture = 0
        self.config = UIConfigs()
        self.thread = None
        self.running = False

        self.init_gpio()

    def init_gpio(self):
        print('Initializing GPIO')

        if self.running:
            print('Wait for thread to end...')
            self.running = False
            self.thread.join()
            print('Thread stopped')

        # dht11
        dth11_pin_name = self.config.read('input-dht-pin')
        if dth11_pin_name:
            if self.sensor != None:
                # clean up the sensor
                self.sensor.exit()
            dth11_pin = Util.get_pin(dth11_pin_name)
            self.sensor = adafruit_dht.DHT11(dth11_pin, use_pulseio=False)
        # light gpio
        self.light = None
        light_pin_name = self.config.read('input-light-pin')
        if light_pin_name:
            light_pin = Util.get_pin(light_pin_name)
            self.light = digitalio.DigitalInOut(light_pin)
            self.light.direction = digitalio.Direction.OUTPUT
            self.light.value = False
        # fan gpio
        self.fan = None
        fan_pin_name = self.config.read('input-fan-pin')
        if fan_pin_name:
            fan_pin = Util.get_pin(fan_pin_name)
            self.fan = digitalio.DigitalInOut(fan_pin)
            self.fan.direction = digitalio.Direction.OUTPUT
            self.fan.value = False
        # wind gpio
        self.wind = None
        wind_pin_name = self.config.read('input-wind-pin')
        if wind_pin_name:
            wind_pin = Util.get_pin(wind_pin_name)
            self.wind = digitalio.DigitalInOut(wind_pin)
            self.wind.direction = digitalio.Direction.OUTPUT
            self.wind.value = False
        # pump gpio
        self.pump = None
        pump_pin_name = self.config.read('input-pump-pin')
        if pump_pin_name:
            pump_pin = Util.get_pin(pump_pin_name)
            self.pump = digitalio.DigitalInOut(pump_pin)
            self.pump.direction = digitalio.Direction.OUTPUT
            self.pump.value = False
        
        self.running = True
        self.thread = Thread(target=self.read_sensors)
        self.thread.start()

    def read_sensors(self):
        while self.running:
            try:
                temperature, humidity = self.read_dht11()
                self.temperature = temperature
                self.humidity = humidity
                self.soil_moisture = self.read_soil_sensor()
                insert_sensor_data(temperature, humidity, self.soil_moisture)
                print('dht11:', temperature, humidity)
            except Exception as e:
                print('Error reading sensors:', e)
                self.temperature = 0
                self.humidity = 0
                self.soil_moisture = 0
            sleep(5)
    
    def read_dht11(self):
        temperature = self.sensor.temperature
        humidity = self.sensor.humidity
        return temperature, humidity
    
    def read_soil_sensor(self):
        return random.uniform(0, 50)
    
    def set_light(self, state):
        if self.light is None:
            return
        if self.light == state:
            return
        self.light.value = state
        insert_action('light', state)
        print('Light set to', state)
    
    def set_fan(self, state):
        if self.fan is None:
            return
        if self.fan == state:
            return
        self.fan.value = state
        insert_action('fan', state)
        print('Fan set to', state)
    
    def set_wind(self, state):
        if self.wind is None:
            return
        if self.wind == state:
            return
        self.wind.value = state
        insert_action('wind', state)
        print('Wind set to', state)

    def set_pump(self, state):
        if self.pump is None:
            return
        if self.pump == state:
            return
        self.pump.value = state
        insert_action('pump', state)
        print('Pump set to', state)
    
    def take_photo(self):
        print('Taking photo...')
        file_name = 'photo_' + datetime.now().strftime('%Y-%m-%d') + '.jpg'
        os.system('rpicam-still --output ./static/photos/' + file_name)

if __name__ == '__main__':
    hardware = Hardware()
    hardware.init_gpio()
    while True:
        cmd = input('Enter command: ')
        if cmd == 'light on':
            hardware.set_light(True)
        elif cmd == 'light off':
            hardware.set_light(False)
        elif cmd == 'fan on':
            hardware.set_fan(True)
        elif cmd == 'fan off':
            hardware.set_fan(False)
        elif cmd == 'wind on':
            hardware.set_wind(True)
        elif cmd == 'wind off':
            hardware.set_wind(False)
        elif cmd == 'pump on':
            hardware.set_pump(True)
        elif cmd == 'pump off':
            hardware.set_pump(False)