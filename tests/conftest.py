import pytest

from mock import MagicMock, PropertyMock
from itertools import cycle


@pytest.fixture
def GPIO():
    mock = MagicMock()
    mock.setup = MagicMock()
    type(mock).HIGH = PropertyMock(return_value=1)
    type(mock).LOW = PropertyMock(return_value=0)
    type(mock).IN = PropertyMock(return_value=1)
    type(mock).OUT = PropertyMock(return_value=0)
    type(mock).PUD_UP = PropertyMock(return_value=1)
    type(mock).PUD_DOWN = PropertyMock(return_value=0)
    mock.output = MagicMock()
    mock.input = MagicMock()
    return mock


@pytest.fixture
def door_controller():
    from hocuspocus.door_controller import DoorController
    return MagicMock(spec=DoorController)


@pytest.fixture
def result_cycler():
    """
    Creates a function that will cycle through the given arguments each
    time the callback function is called. This is great for Mock side effects
    where you need the mocked function to return something different each
    time it's called.
    """
    def wrapper(*args):
        cycler = cycle(args)

        def callback(*args, **kwargs):
            return next(cycler)

        return callback

    return wrapper
