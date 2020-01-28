import numpy as np

from push4.utils import median_absolute_deviation


def test_mad():
    x = np.array([1, 2, 3])
    assert median_absolute_deviation(x) == 1.0

    x = np.array([1, 3, 10, 100, 101])
    assert median_absolute_deviation(x) == 9.0

    assert np.isnan(median_absolute_deviation(np.array([])))
