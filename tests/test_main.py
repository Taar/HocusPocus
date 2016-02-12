import os
import pytest
import shutil

from contextlib import contextmanager
from mock import MagicMock, patch, PropertyMock, call
from itertools import cycle, count


@pytest.fixture
def real_pid_file():

    # Create a contextmanager for easy clean up of the created file
    @contextmanager
    def wrapper():
        path = '/tmp/door_controller.pid'
        with open(path, 'w'):
            pass

        yield path
        os.remove(path)

    return wrapper


@pytest.fixture
def real_empty_dir():

    # Create a contextmanager for easy clean up of the created file
    @contextmanager
    def wrapper():
        path = '/tmp/door_controller/'
        os.mkdir(path)
        yield path
        shutil.rmtree(path)

    return wrapper


@pytest.fixture
def relay_error():

    tests = cycle([1, 2, 3])
    codes = cycle(['0 1', '0 2', '0 3'])

    def tests_cb():
        return next(tests)

    def codes_cb():
        return next(codes)

    mock = MagicMock()
    mock.codes = MagicMock()
    type(mock.codes).relay = PropertyMock(return_value=0)
    type(mock.codes).test = PropertyMock(side_effect=tests_cb)
    type(mock).message = PropertyMock(return_value='Mock Message')
    type(mock).code = PropertyMock(side_effect=codes_cb)
    return mock


@pytest.fixture
def relay_error_factory():

    def callback(codes, relay, test, message):
        mock = MagicMock()
        mock.codes = MagicMock()
        type(mock.codes).relay = PropertyMock(return_value=relay)
        type(mock.codes).test = PropertyMock(return_value=test)
        type(mock).message = PropertyMock(return_value=message)
        type(mock).code = PropertyMock(return_value=codes)
        return mock

    return callback


@pytest.fixture
def relay_error_generator(relay_error_factory):

    def generator(params):
        cycler = cycle(params)

        def callback(*args, **kwargs):
            return relay_error_factory(*next(cycler))

        return callback

    return generator


def pid_contains(pid_path, expected_lines):
    __tracebackhide__ = True
    with open(pid_path, 'r') as pid:
        lines = [line for line in pid.readlines()]

    if not len(lines) == len(expected_lines):
        pytest.fail(
            ("pid file does not contain the same expected lines.\n"
             "pid file CONTAINS: {lines}\n"
             "but EXPECTED: {expected}"
             ).format(lines=lines, expected=expected_lines)
        )

    for number, line, expected in zip(count(start=1), lines, expected_lines):
        if not line == expected:
            line = line.encode('unicode-escape')
            expected = expected.encode('unicode-escape')
            pytest.fail(
                ("Line {number} does not match expected line\n"
                 "Got: {line}\n"
                 "Expected: {expected}"
                 ).format(number=number, line=line, expected=expected)
            )


class TestPidFileExists():

    def test_pid_file_exists(self, real_pid_file):
        from hocuspocus.main import pid_file_exists
        with real_pid_file() as path:
            assert pid_file_exists(path)

    def test_pid_is_file_not_dir(self, real_empty_dir):
        from hocuspocus.main import pid_file_exists
        with real_empty_dir() as path:
            assert not pid_file_exists(path)

    def test_pid_file_does_not_exist(self):
        from hocuspocus.main import pid_file_exists
        assert not pid_file_exists('/some/random/path')


class TestCheckRelays():

    @pytest.yield_fixture(autouse=True)
    def patch_functions(self):
        sleep_patacher = patch('time.sleep')
        self.sleep = sleep_patacher.start()
        yield
        sleep_patacher.stop()

    def test_relay_state_are_in_expected_state(self,
                                               door_controller,
                                               result_cycler):
        from hocuspocus.main import check_relays

        door_controller.test_relay_state = MagicMock(
            side_effect=result_cycler(True, True))

        relay_state = check_relays(door_controller,
                                   1,
                                   first=door_controller.high,
                                   second=door_controller.high)
        assert relay_state.code == '0 1'
        assert relay_state.codes.relay == 0
        assert relay_state.codes.test == 1
        assert relay_state.message == "Relays are in expected states."

    def test_first_relay_state_is_in_unexpected_state(self,
                                                      door_controller,
                                                      result_cycler):
        from hocuspocus.main import check_relays

        door_controller.test_relay_state = MagicMock(
            side_effect=result_cycler(False, True))

        relay_state = check_relays(door_controller,
                                   1,
                                   first=door_controller.high,
                                   second=door_controller.high)
        assert relay_state.code == '1 1'
        assert relay_state.codes.relay == 1
        assert relay_state.codes.test == 1
        assert relay_state.message == (
            "Relay Failure on test number [1]: "
            "Relays in wrong state: [first]"
        )

    def test_second_relay_state_is_in_unexpected_state(self,
                                                       door_controller,
                                                       result_cycler):
        from hocuspocus.main import check_relays

        door_controller.test_relay_state = MagicMock(
            side_effect=result_cycler(True, False))

        relay_state = check_relays(door_controller,
                                   1,
                                   first=door_controller.high,
                                   second=door_controller.high)
        assert relay_state.code == '2 1'
        assert relay_state.codes.relay == 2
        assert relay_state.codes.test == 1
        assert relay_state.message == (
            "Relay Failure on test number [1]: "
            "Relays in wrong state: [second]"
        )

    def test_both_relays_states_are_in_a_unexpected_state(self,
                                                          door_controller,
                                                          result_cycler):
        from hocuspocus.main import check_relays

        door_controller.test_relay_state = MagicMock(
            side_effect=result_cycler(False, False))

        relay_state = check_relays(door_controller,
                                   1,
                                   first=door_controller.high,
                                   second=door_controller.high)
        assert relay_state.code == '3 1'
        assert relay_state.codes.relay == 3
        assert relay_state.codes.test == 1
        assert relay_state.message == (
            "Relay Failure on test number [1]: "
            "Relays in wrong state: [both]"
        )


class TestLogError():

    def test_logging_error_message_into_pid_file(self,
                                                 real_pid_file,
                                                 relay_error_factory):
        from hocuspocus.main import log_error

        relay_error = relay_error_factory('2 1', 2, 1, "Mock Message")

        with real_pid_file() as path:
            log_error(path, relay_error)
            pid_contains(path, ['2 1\n', 'Mock Message'])


class TestUnlockDoor():

    @pytest.yield_fixture(autouse=True)
    def patch_functions(self):
        check_relays_patcher = patch('hocuspocus.main.check_relays')
        self.check_relays = check_relays_patcher.start()
        yield
        check_relays_patcher.stop()

    def test_no_relay_failures_should_return_none(self,
                                                  door_controller,
                                                  relay_error):

        from hocuspocus.main import unlock_door
        self.check_relays.return_value = relay_error
        assert unlock_door(door_controller) is None

    def test_first_relay_check_fails(self,
                                     door_controller,
                                     relay_error_generator):
        from hocuspocus.main import unlock_door
        self.check_relays.side_effect = relay_error_generator(
            [
                ('2 1', 2, 1, "Mock Message"),
            ]
        )
        relay_error = unlock_door(door_controller)
        assert relay_error.codes.relay == 2
        assert relay_error.codes.test == 1
        self.check_relays.assert_called_with(
            door_controller,
            1,
            first=door_controller.low,
            second=door_controller.low
        )

    def test_door_is_held_open_for_the_given_seconds(self,
                                                     door_controller,
                                                     relay_error_generator):
        from hocuspocus.main import unlock_door
        self.check_relays.side_effect = relay_error_generator(
            [
                ('0 1', 0, 1, "Mock Message"),
            ]
        )
        assert unlock_door(door_controller, ms=10000) is None
        call_list = door_controller.mock_calls
        assert call_list == [
            call.relays(activate=True),
            call.turn_off_led(door_controller.red_pin),
            call.activate_pin(door_controller.green_pin, ms=5000),
            call.relays(activate=False),
            call.turn_on_led(door_controller.red_pin),
        ]

    def test_second_relay_check_fails(self,
                                      door_controller,
                                      relay_error_generator):
        from hocuspocus.main import unlock_door
        self.check_relays.side_effect = relay_error_generator(
            [
                ('0 1', 0, 1, "Mock Message"),
                ('2 2', 2, 2, "Mock Message"),
            ]
        )
        relay_error = unlock_door(door_controller)
        assert relay_error.codes.relay == 2
        assert relay_error.codes.test == 2
        self.check_relays.assert_called_with(
            door_controller,
            2,
            first=door_controller.high,
            second=door_controller.high
        )

    def test_relays_are_deactivated_after_green_led_is_shown(
            self, door_controller, relay_error_generator):

        from hocuspocus.main import unlock_door
        self.check_relays.side_effect = relay_error_generator(
            [
                ('0 1', 0, 1, "Mock Message"),
            ]
        )
        assert unlock_door(door_controller, ms=10000) is None
        call_list = door_controller.mock_calls
        assert call_list == [
            call.relays(activate=True),
            call.turn_off_led(door_controller.red_pin),
            call.activate_pin(door_controller.green_pin, ms=5000),
            call.relays(activate=False),
            call.turn_on_led(door_controller.red_pin),
        ]

    def test_third_relay_check_fails(self,
                                     door_controller,
                                     relay_error_generator):

        from hocuspocus.main import unlock_door
        self.check_relays.side_effect = relay_error_generator(
            [
                ('0 1', 0, 1, "Mock Message"),
                ('0 2', 0, 1, "Mock Message"),
                ('2 3', 2, 3, "Mock Message"),
            ]
        )
        relay_error = unlock_door(door_controller)
        assert relay_error.codes.relay == 2
        assert relay_error.codes.test == 3

        self.check_relays.assert_called_with(
            door_controller,
            3,
            first=door_controller.low,
            second=door_controller.low
        )

    def test_on_failure_try_to_recover_on_first_check(self,
                                                      door_controller,
                                                      relay_error_generator):
        from hocuspocus.main import unlock_door
        self.check_relays.side_effect = relay_error_generator(
            [
                ('2 1', 2, 1, "Mock Message"),
            ]
        )
        relay_error = unlock_door(door_controller)
        assert relay_error.codes.relay == 2
        assert relay_error.codes.test == 1

        call_list = door_controller.mock_calls
        assert call_list == [
            call.relays(activate=False),
        ]

    def test_on_failure_try_to_recover_on_second_check(self,
                                                       door_controller,
                                                       relay_error_generator):
        from hocuspocus.main import unlock_door
        self.check_relays.side_effect = relay_error_generator(
            [
                ('0 1', 0, 1, "Mock Message"),
                ('2 2', 2, 2, "Mock Message"),
            ]
        )
        relay_error = unlock_door(door_controller)
        assert relay_error.codes.relay == 2
        assert relay_error.codes.test == 2

        call_list = door_controller.mock_calls
        assert call_list == [
            call.relays(activate=True),
            call.relays(activate=False),
        ]

    def test_on_failure_try_to_recover_on_third_check(self,
                                                      door_controller,
                                                      relay_error_generator):
        from hocuspocus.main import unlock_door
        self.check_relays.side_effect = relay_error_generator(
            [
                ('0 1', 0, 1, "Mock Message"),
                ('0 1', 0, 1, "Mock Message"),
                ('2 3', 2, 3, "Mock Message"),
            ]
        )
        relay_error = unlock_door(door_controller)
        assert relay_error.codes.relay == 2
        assert relay_error.codes.test == 3

        call_list = door_controller.mock_calls
        assert call_list == [
            call.relays(activate=True),
            call.turn_off_led(door_controller.red_pin),
            call.activate_pin(door_controller.green_pin, ms=5000),
            call.relays(activate=False),
            call.turn_on_led(door_controller.red_pin),
            call.relays(activate=False),
        ]


class TestDisplayErrorCode():

    def test_relay_error_1_1(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('1 1', 1, 1, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_1_2(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('1 2', 1, 2, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_1_3(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('1 3', 1, 3, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_2_1(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('2 1', 2, 1, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_2_2(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('2 2', 2, 2, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_2_3(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('2 3', 2, 3, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_3_1(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('3 1', 3, 1, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_3_2(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('3 2', 3, 2, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_3_3(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('3 3', 3, 3, "Mock Message")

        loop = cycle((True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list

    def test_relay_error_loop(self, door_controller, relay_error_factory):

        from hocuspocus.main import display_error_code

        relay_error = relay_error_factory('1 1', 1, 1, "Mock Message")

        loop = cycle((True, True, False))
        display_error_code(relay_error, door_controller, loop=loop)

        call_list = door_controller.mock_calls

        expected_calls = [
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=2000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
            call.activate_pin(
                door_controller.red_pin,
                ms=1000,
                suffix_ms=2000
            ),
        ]

        assert expected_calls == call_list
