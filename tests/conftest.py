import os

import pytest


@pytest.fixture(scope='session')
def fpath_test_data() -> str:
    fpath_test_dir = os.path.dirname(__file__)
    return os.path.join(fpath_test_dir, 'test_data')
