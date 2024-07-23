import os

import pytest


@pytest.fixture(scope='session')
def fpath_test_data() -> str:
    fpath_test_dir = os.path.dirname(__file__)
    return os.path.join(fpath_test_dir, 'test_data')

@pytest.fixture(scope='session')
def fpath_nb_dir(
    fpath_test_data: str,
) -> str:
    return os.path.join(fpath_test_data, 'notebooks')
