import board
from database import fetch_actions
from datetime import datetime, timedelta
import configparser

class Util:
    @staticmethod
    def get_pins():
        pins = [pin for pin in dir(board) if pin.startswith('D')]
        return pins

    @staticmethod
    def get_pin(pin):
        return getattr(board, pin)
    
    def fetch_and_separete_actions(dt_from, dt_to):
        dt_from = dt_from + timedelta(days=1)
        dt_to = dt_to + timedelta(days=1)
        actions = fetch_actions(dt_from, dt_to)
        actors = {}
        for action in actions:
            # name the variables for better understanding
            time = action[1]
            actor = action[2]
            state = action[3]

            if actor not in actors:
                # if the actor is not in the dictionary, add it
                actors[actor] = []
                if state == 0:
                    # if the actor is off, add a dummy entry
                    actors[actor].append({'dt_from': datetime.strftime(dt_from, '%Y-%m-%dT%H:%M:%S'), 'dt_to': time})
                else:
                    actors[actor].append({'dt_from': time, 'dt_to': None})
            else:
                if state == 1:
                    if actors[actor][-1]['dt_to'] is None:
                        # if the actor is already on, remove the last entry
                        actors[actor].pop()
                    actors[actor].append({'dt_from': time, 'dt_to': None})
                else:
                    actors[actor][-1]['dt_to'] = time

        # check if some actor is still on
        for actor in actors:
            if actors[actor][-1]['dt_to'] is None:
                actors[actor][-1]['dt_to'] = datetime.strftime(dt_to, '%Y-%m-%dT%H:%M:%S')
        return actors
    
class UIConfigs:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UIConfigs, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self):
        self.config_file_name = 'config.ini'
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_name)

    def write(self, name, value):
        self.config['ui-configuration'][name] = value
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
    
    def read(self, name):
        if name not in self.config['ui-configuration']:
            return None
        return self.config['ui-configuration'][name]
    
    def read_all(self):
        config = {name: value for name, value in self.config['ui-configuration'].items()}
        return config