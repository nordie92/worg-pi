import board

class Util:
    @staticmethod
    def get_pins():
        pins = [pin for pin in dir(board) if pin.startswith('D')]
        return pins

    def get_pin(pin):
        return getattr(board, pin)