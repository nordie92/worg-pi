from threading import Thread
from util import UIConfigs
from hardware import Hardware
from time import sleep
from datetime import time, datetime, timedelta

class Automation:
    def __init__(self):
        self.config = UIConfigs()
        self.hardware = Hardware()
        self.pump_off_time = None
        self.pump_pause_time = None
        self.next_photo_time = None
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.set_next_photo_time()
            self.thread = Thread(target=self.run)
            self.thread.start()
    
    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
    
    def restart(self):
        self.stop()
        self.start()

    def run(self):
        while self.running:
            try:
                # light
                if self.hardware.light:
                    latest_state_is_on = self.get_latest_state(self.config.read('input-light-off'), self.config.read('input-light-on'))
                    if not latest_state_is_on:
                        if self.hardware.light.value:
                            self.hardware.set_light(False)
                    else:
                        if not self.hardware.light.value:
                            self.hardware.set_light(True)

                # fan
                if self.hardware.fan:
                    if self.hardware.fan.value:
                        fan_off_temp = float(self.config.read('input-fan-off'))
                        if self.hardware.temperature < fan_off_temp:
                            self.hardware.set_fan(False)
                    else:
                        fan_on_temp = float(self.config.read('input-fan-on'))
                        if self.hardware.temperature > fan_on_temp:
                            self.hardware.set_fan(True)
                
                # wind
                if self.hardware.wind:
                    latest_state_is_on = self.get_latest_state(self.config.read('input-wind-off'), self.config.read('input-wind-on'))
                    if not latest_state_is_on:
                        if self.hardware.wind.value:
                            self.hardware.set_wind(False)
                    else:
                        if not self.hardware.wind.value:
                            self.hardware.set_wind(True)
                
                # pump
                if self.hardware.pump:
                    # set pump pause time to None if pause time is over
                    if self.pump_pause_time and datetime.now() >= self.pump_pause_time:
                        self.pump_pause_time = None

                    pump_on_hum = float(self.config.read('input-pump-on'))
                    pump_duration = float(self.config.read('input-pump-on-duration'))
                    pump_pause_time = float(self.config.read('input-pump-pause-time'))

                    if not self.hardware.pump.value:
                        if self.pump_pause_time is None and self.pump_off_time is None and self.hardware.soil_moisture < pump_on_hum:
                            self.pump_off_time = datetime.now() + timedelta(seconds=pump_duration)
                            self.hardware.set_pump(True)
                    else:
                        if self.pump_off_time and datetime.now() >= self.pump_off_time:
                            self.pump_pause_time = datetime.now() + timedelta(minutes=pump_pause_time)
                            self.pump_off_time = None
                            self.hardware.set_pump(False)
                
                # take photo
                if datetime.now() >= self.next_photo_time:
                    self.hardware.take_photo()
                    self.set_next_photo_time()
                
                
            except Exception as e:
                print(e)
            finally:
                sleep(1)
            
        self.pump_pause_time = None
        self.hardware.set_light(False)
        self.hardware.set_fan(False)
        self.hardware.set_wind(False)
        self.hardware.set_pump(False)

    def set_next_photo_time(self):
        photo_time = self.config.read('input-picture-capture-time')
        self.next_photo_time = datetime.now().replace(hour=int(photo_time.split(':')[0]), minute=int(photo_time.split(':')[1]), second=0)
        if self.next_photo_time < datetime.now():
            self.next_photo_time += timedelta(days=1)
    
    def get_latest_state(self, str_off_times, str_on_times):
        off_times = str_off_times.replace(' ', '').split(',')
        on_times = str_on_times.replace(' ', '').split(',')
        off_dts = [datetime.combine(datetime.now(), time.fromisoformat(off_time)) for off_time in off_times]
        on_dts = [datetime.combine(datetime.now(), time.fromisoformat(on_time)) for on_time in on_times]
        # get the latest time from off and on
        latest_time = datetime.combine(datetime.now(), time(0, 0))
        latest_state_is_on = False
        for off_dt in off_dts:
            if off_dt > latest_time and off_dt <= datetime.now():
                latest_time = off_dt
                latest_state_is_on = False
        for on_dt in on_dts:
            if on_dt > latest_time and on_dt <= datetime.now():
                latest_time = on_dt
                latest_state_is_on = True
        return latest_state_is_on