import argparse
import configparser
from main import main
from door_controller import DoorController
import Adafruit_BBIO.GPIO as GPIO


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Door controller daemon')
    parser.add_argument('ini_file', type=argparse.FileType('r'))
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read_file(args.ini_file)

    door_controller = DoorController(GPIO)

    main(
        config.get('paths', 'pid_file'),
        config.get('paths', 'error_file'),
        door_controller
    )
