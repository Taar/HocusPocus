import time
from collections import namedtuple


Relay = namedtuple('Relay', 'read engage')


class DoorController():
    """
    GPIO Pins used:
        Relay_1: Read=46 & Engage=47
        Relay_1: Read=P8_16 & Engage=P8_15

        Relay_2: Read=65 & Engage=27
        Relay_2: Read=P8_18 & Engage=P8_17

        Green_LED: 45
        Green_LED: P8_11

        Read_LED: 69
        Read_LED: P8_9
    """
    relay_1 = Relay('P8_16', 'P8_15')
    relay_2 = Relay('P8_18', 'P8_17')
    green_pin = 'P8_11'
    red_pin = 'P8_9'

    def __init__(self, GPIO):
        self.GPIO = GPIO

        # Relay_1: Read
        self.GPIO.setup(
            self.relay_1.read,
            self.GPIO.IN,
            pull_up_down=self.GPIO.PUD_DOWN
        )
        # Relay_2: Read
        self.GPIO.setup(
            self.relay_2.read,
            self.GPIO.IN,
            pull_up_down=self.GPIO.PUD_DOWN
        )

        # Relay_1: Engage
        self.GPIO.setup(
            self.relay_1.engage,
            self.GPIO.OUT,
            pull_up_down=self.GPIO.PUD_DOWN
        )
        # Relay_2: Engage
        self.GPIO.setup(
            self.relay_2.engage,
            self.GPIO.OUT,
            pull_up_down=self.GPIO.PUD_DOWN
        )

        # Red_LED
        self.GPIO.setup(
            self.red_pin,
            self.GPIO.OUT,
            pull_up_down=self.GPIO.PUD_DOWN
        )
        # Green_LED
        self.GPIO.setup(
            self.green_pin,
            self.GPIO.OUT,
            pull_up_down=self.GPIO.PUD_DOWN
        )

    @property
    def high(self):
        return self.GPIO.HIGH

    @property
    def low(self):
        return self.GPIO.LOW

    def clean_up(self):
        self.turn_off_led(self.green_pin)
        self.turn_off_led(self.red_pin)
        self.relays(False)

    def turn_on_led(self, pin):
        self.GPIO.output(pin, self.high)

    def turn_off_led(self, pin):
        self.GPIO.output(pin, self.low)

    def test_relay_state(self, relay, expected):
        """
        returns True if the relay is in the spected state
        """
        return self.GPIO.input(relay) == expected

    def relays(self, activate=True):
        output = self.high if activate else self.low
        self.GPIO.output(self.relay_1.engage, output)
        self.GPIO.output(self.relay_2.engage, output)

    def activate_pin(self, pin, ms=500, suffix_ms=0):
        """
        Activate pin and hold HIGH for the X milliseconds.

        pin - the pin to activate
        ms - (default: 500ms) time to hold pin high
        suffix_ms - (default: 0ms) time to wait after setting pin low
        """

        # prevent sleeping for less than half a second
        if ms < 500:
            ms = 500

        self.GPIO.output(pin, self.GPIO.HIGH)
        time.sleep(ms/1000)  # convert milliseconds to seconds
        self.GPIO.output(pin, self.GPIO.LOW)
        if suffix_ms > 0:
            time.sleep(suffix_ms/1000)
