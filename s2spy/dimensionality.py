"""s2spy dimensionality reduction module.

A module handling dimensionality reduction tasks, which provides a
collection of dimensionality reduction approaches.
"""

def RGDR(series, lag_shift: int = 0):
    """Wrapper for Response Guided Dimensionality Reduction function.

    Configure RGDR operations using this function. It manages input training
    data it also invokes the RGDR operator for the relevant correlation
    and clustering processes via the RGDR module.

    Args:
        series: Target timeseies.
        field: Target fields.
        lag_shift: Number of lag shifts that will be tested.
    """
    # To do: invoke RGDR functions without execution.
    # e.g. import functools
    # RGDR = functools.partial(s2s.RGDR.operator, series, lag_shift)
    # return RGDR
    raise NotImplementedError

def PCA():
    """Wrapper for Principle Component Analysis."""
    raise NotImplementedError

def MCA():
    """Wrapper for Maximum Covariance Analysis."""
    raise NotImplementedError
