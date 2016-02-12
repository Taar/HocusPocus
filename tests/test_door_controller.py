from mock import call, patch


class TestDoorController():

    def test_init_setup(self, GPIO):
        from hocuspocus.door_controller import DoorController

        door_controller = DoorController(GPIO)
        expected_calls = [
            call.setup(
                door_controller.relay_1.read,
                GPIO.IN,
                pull_up_down=GPIO.PUD_DOWN
            ),
            call.setup(
                door_controller.relay_2.read,
                GPIO.IN,
                pull_up_down=GPIO.PUD_DOWN
            ),
            call.setup(
                door_controller.relay_1.engage,
                GPIO.OUT,
                pull_up_down=GPIO.PUD_DOWN
            ),
            call.setup(
                door_controller.relay_2.engage,
                GPIO.OUT,
                pull_up_down=GPIO.PUD_DOWN
            ),
            call.setup(
                door_controller.red_pin,
                GPIO.OUT,
                pull_up_down=GPIO.PUD_DOWN
            ),
            call.setup(
                door_controller.green_pin,
                GPIO.OUT,
                pull_up_down=GPIO.PUD_DOWN
            ),
        ]

        for expected, actual in zip(expected_calls, GPIO.mock_calls):
            assert actual == expected


class TestActivatePin():

    def test_default_behavour(self, GPIO):
        with patch('time.sleep') as mock_sleep:
            from hocuspocus.door_controller import DoorController

            door_controller = DoorController(GPIO)
            GPIO.reset_mock()
            door_controller.activate_pin('PIN')
            assert len(GPIO.mock_calls) == 2
            assert GPIO.mock_calls[0] == call.output('PIN', GPIO.HIGH)
            assert mock_sleep.call_count == 1
            assert mock_sleep.called
            assert GPIO.mock_calls[1] == call.output('PIN', GPIO.LOW)

    def test_ms_kwarg(self, GPIO):
        with patch('time.sleep') as mock_sleep:
            from hocuspocus.door_controller import DoorController

            ms = 1000
            door_controller = DoorController(GPIO)
            door_controller.activate_pin('PIN', ms)
            assert mock_sleep.call_count == 1
            assert mock_sleep.called
            mock_sleep.assert_called_with(1.0)

    def test_ms_kwarg_less_than_500(self, GPIO):
        with patch('time.sleep') as mock_sleep:
            from hocuspocus.door_controller import DoorController

            door_controller = DoorController(GPIO)
            door_controller.activate_pin('PIN', 499)
            assert mock_sleep.call_count == 1
            assert mock_sleep.called
            mock_sleep.assert_called_with(0.5)

            mock_sleep.reset_mock()

            door_controller.activate_pin('PIN', 0)
            assert mock_sleep.call_count == 1
            assert mock_sleep.called
            mock_sleep.assert_called_with(0.5)

    def test_suffix_ms_delay(self, GPIO):
        with patch('time.sleep') as mock_sleep:
            from hocuspocus.door_controller import DoorController

            door_controller = DoorController(GPIO)
            door_controller.activate_pin('PIN', ms=1000, suffix_ms=500)
            assert mock_sleep.call_count == 2
            mock_sleep.assert_has_calls([call(1), call(0.5)])


class TestRelays():

    def test_setting_relays_high(self, GPIO):
        from hocuspocus.door_controller import DoorController
        door_controller = DoorController(GPIO)
        GPIO.reset_mock()
        door_controller.relays(activate=True)

        expected_calls = [
            call.output(door_controller.relay_1.engage, GPIO.HIGH),
            call.output(door_controller.relay_2.engage, GPIO.HIGH),
        ]

        assert GPIO.mock_calls == expected_calls

    def test_setting_relays_low(self, GPIO):
        from hocuspocus.door_controller import DoorController
        door_controller = DoorController(GPIO)
        GPIO.reset_mock()
        door_controller.relays(activate=False)

        expected_calls = [
            call.output(door_controller.relay_1.engage, GPIO.LOW),
            call.output(door_controller.relay_2.engage, GPIO.LOW),
        ]

        assert GPIO.mock_calls == expected_calls


class TestTestRelayState():

    def test_high_expected(self, GPIO):
        from hocuspocus.door_controller import DoorController
        door_controller = DoorController(GPIO)
        GPIO.input.return_value = 1
        assert door_controller.test_relay_state('PIN', GPIO.HIGH)

    def test_high_unexpected(self, GPIO):
        from hocuspocus.door_controller import DoorController
        door_controller = DoorController(GPIO)
        GPIO.input.return_value = 1
        assert not door_controller.test_relay_state('PIN', GPIO.LOW)
