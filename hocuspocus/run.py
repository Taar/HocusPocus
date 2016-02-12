from main import main
from door_controller import DoorController
import Adafruit_BBIO.GPIO as GPIO

door_controller = DoorController(GPIO)

main(
    '/tmp/door_controller.pid',
    '/tmp/door_controller_error.txt',
    door_controller
)
