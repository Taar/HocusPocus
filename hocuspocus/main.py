import os
import sys
import time
import signal
import threading

from collections import namedtuple
from itertools import cycle
from functools import partial


Codes = namedtuple('Codes', 'relay test')


class RelayError():

    failed_relay = {
        '1': 'first',
        '2': 'second',
        '3': 'both',
    }

    def __init__(self, code):
        self.code = code
        self.codes = Codes(*map(int, code.split()))
        if self.codes.relay == 0:
            self.message = "Relays are in expected states."
        else:
            self._message_template = (
                "Relay Failure on test number [{test}]: "
                "Relays in wrong state: [{code}]"
            )
            self.message = self._message_template.format(
                test=self.codes.test,
                code=self.failed_relay[str(self.codes.relay)]
            )


def pid_file_exists(path):
    """
    Checks to make sure the given path is a file and exists in the file system
    """
    return os.path.isfile(path)


def log_error(path, relay_error):
    """
    Logs the given RelayError instance in the pid file
    TODO: log to a another file
    TODO: handle case where pid doesn't exist
    """
    with open(path, 'wb') as pid:
        pid.write(bytearray("{}\n".format(relay_error.code), 'utf-8'))
        pid.write(bytearray(relay_error.message, 'utf-8'))


def check_relays(door_controller, test, **kwargs):
    """
    Compares the expected state against the state of the relays in the
    door controller. Returns an ErrorCode instance if one or more of the
    expected states aren't correct. If the states match what is expected than
    an ErrorCode object with the codes of '0 0' will be returned.
    """

    # wait 200 milliseconds because the relays have a slight delay
    ms = kwargs.get('ms', 1000)
    if ms > 0:
        time.sleep(ms/1000)

    first = kwargs.get('first', door_controller.high)
    second = kwargs.get('second', door_controller.high)

    relay_one = door_controller.relay_1.read
    relay_two = door_controller.relay_2.read

    relay = 0

    if not door_controller.test_relay_state(relay_one, first):
        relay += 1

    if not door_controller.test_relay_state(relay_two, second):
        relay += 2

    return RelayError("{relay} {test}".format(test=test, relay=relay))


def create_pid_file(path):
    with open(path, 'w+') as f:
        f.write(str(os.getpid()))


def remove_pid_file(path):
    if os.path.exists(path):
        os.remove(path)


def unlock_door(door_controller, ms=5000):
    """
    Unlocks the door. If there is an issue with one of the relays it'll
    return a `RelayError` with information about the failure. Otherwise
    it'l return `None`.
    """
    relay_error = check_relays(door_controller, 1,
                               first=door_controller.low,
                               second=door_controller.low)

    if relay_error.codes.relay > 0:
        door_controller.relays(activate=False)
        return relay_error

    door_controller.relays(activate=True)

    relay_error = check_relays(door_controller, 2,
                               first=door_controller.high,
                               second=door_controller.high)

    if relay_error.codes.relay > 0:
        door_controller.relays(activate=False)
        return relay_error

    door_controller.turn_off_led(door_controller.red_pin)

    door_controller.activate_pin(door_controller.green_pin, ms=5000)

    door_controller.relays(activate=False)

    door_controller.turn_on_led(door_controller.red_pin)

    relay_error = check_relays(door_controller, 3,
                               first=door_controller.low,
                               second=door_controller.low)

    if relay_error.codes.relay > 0:
        door_controller.relays(activate=False)
        return relay_error

    return None


def display_error_code(relay_error, door_controller, **kwargs):
    """
    Displays the error code given by the `relay_error` object by flashing
    a led.

    `relay_error` - RelayError

    `door_controller` - DoorController

    [`loop`] - should be an iterator that contains turthy or falsy values
    if it isn't given the default iterator will be used which will return
    True, False making the while loop only loop once

    The Red Led on error will flash to display the error codes:

    - Each flash consists of being held high for 500ms and low for 500ms

    - Hold led high for 1 second (Start of the error code)

    - Hold Low for 1 second

    - the second part is the replay that failed the check
        - 1 flash being the first
        - 2 flashes being the second
        - 3 flashes being both

    - Hold Low for 1 second

    - first part is where in the script it failed
        - 1 flash being the first check
        - 2 flashes being the second check
        - 3 flashes being the third check

    - Hold Low for 1 second
    """

    loop = kwargs.get('loop', cycle((True,)))

    while next(loop):
        door_controller.activate_pin(
            door_controller.red_pin, ms=2000, suffix_ms=2000)

        for _ in range(0, relay_error.codes.relay - 1):
            door_controller.activate_pin(
                door_controller.red_pin, ms=1000)
        else:
            door_controller.activate_pin(
                door_controller.red_pin, ms=1000, suffix_ms=2000)

        for _ in range(0, relay_error.codes.test - 1):
            door_controller.activate_pin(
                door_controller.red_pin, ms=1000)
        else:
            door_controller.activate_pin(
                door_controller.red_pin, ms=1000, suffix_ms=2000)


class DoorThread(threading.Thread):

    def __init__(self, lock, door_controller, error_path):
        super(DoorThread, self).__init__()
        self.door_controller = door_controller
        self.error_path = error_path
        self.lock = lock

    def run(self):

        print('running')
        available = self.lock.acquire(blocking=False)
        if not available:
            print('resource locked')
            return

        print('unlocking door')
        relay_error = unlock_door(self.door_controller)

        if relay_error:
            log_error(self.error_path, relay_error)
            display_error_code(
                relay_error,
                self.door_controller
            )

        self.lock.release()


# has accuess to the signal number and frame
def handle_usr1(lock, door_controller, error_path, *args):
    print('Handling USR1')
    door_thread = DoorThread(lock, door_controller, error_path)
    door_thread.start()


def exit_gracefully(pid_path, *args):
    remove_pid_file(pid_path)
    sys.exit(1)


def main(pid_path, error_path, door_controller):

    exit_callback = partial(exit_gracefully, pid_path)
    # check SIGINT (ctrl-c)
    signal.signal(signal.SIGINT, exit_callback)
    signal.signal(signal.SIGTERM, exit_callback)

    if os.path.exists(pid_path):
        sys.exit('PID file already exists! ({})'.format(pid_path))

    door_controller.turn_on_led(door_controller.red_pin)

    lock = threading.Lock()

    create_pid_file(pid_path)

    signal.signal(signal.SIGUSR1,
                  partial(handle_usr1, lock, door_controller, error_path))

    print('starting while')
    while True:
        signal.pause()
        print('Processed signal')
