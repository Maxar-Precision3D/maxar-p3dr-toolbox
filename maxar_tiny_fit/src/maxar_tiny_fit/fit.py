"""
Module containing the 'leastsq' function for iterative least squares.
"""
from __future__ import annotations  # noqa

import numpy as np
from numpy.typing import ArrayLike, NDArray
import sys
from typing import Any, Callable, Dict


def leastsq(func: Callable[[NDArray], NDArray],
            params: ArrayLike,
            steps: float | ArrayLike = 1e-03,
            max_iter: int = 10,
            eps: float = 1e-03,
            stop: float = 1e-03) -> Dict[str, Any]:
    """
    Iteratively fit function parameters using Gauss-Newton's method.

    Parameters:
        func:   A function taking the solvable parameters as a Numpy array
                for evaluation. After evaluation the function is returning
                another Numpy array with residuals.
        params: The initial set of parameters.
        steps:  The step length used during differention. Either a scalar
                that is applied to all parameters, or a set of individual
                steps. If a set is given it must have same length as
                the parameter set.
        max_iter: The max number of iteration.
        eps:    Epsilon, if the squared summed errors of the residuals
                are less than this value the fitting is successfully
                terminated.
        stop:   Inter iteration stop condition. If the change of the
                error value between two iterations is lower than this
                threshold the fitting is terminated.

    Returns:
        A dictionary with the result from the fitting.
        {
            'successful': <boolean success value>,
            'message': <human readably description>,
            'iterations': <the number of iterations made>,
            'params': <the parameter set at last iteration>,
            'error': <the sum of squared residual errors>
        }

    """
    params = np.array(params, dtype=np.float64)
    if isinstance(steps, float):
        steps = np.full_like(params, steps)
    else:
        steps = np.array(steps)

    assert params.dtype == np.float64
    assert steps.dtype == np.float64
    assert params.shape == steps.shape

    # TODO: Add support for Levenberg-Marquard.
    return _gauss_newton(func, params, steps, max_iter, eps, stop)


def _gauss_newton(func: Callable[[NDArray], NDArray],
                  params: NDArray,
                  steps: NDArray,
                  max_iter: int,
                  eps: float,
                  stop: float) -> Dict[str, Any]:
    latest_error: float = sys.float_info.max
    for iter in range(max_iter):
        # Compute the residuals, and their error, for the current set of parameters.
        residuals = func(params)
        error: float = np.sum(residuals ** 2)

        # Check for success.
        if error < eps:
            return _result(True, 'Less than eps threshold', iter, params, error)

        # Check relative change in error since latest iteration.
        if abs(latest_error - error) < stop:
            return _result(False, 'Too small change', iter, params, error)

        # Compute the Jacobian.
        J = _Jacobian(func, params, steps)
        JtJ = J.T @ J

        if np.linalg.det(JtJ) < 1e-08:
            return _result(False, 'Singular matrix', iter, params, error)

        # Newton update.
        params -= np.linalg.inv(JtJ) @ J.T @ residuals

        latest_error = error

    # The max number of iterations has passed.
    return _result(False, 'Iteration exceeded', max_iter, params, latest_error)


def _Jacobian(func: Callable[[NDArray], NDArray],
              params: NDArray,
              steps: NDArray) -> NDArray:
    # Construct the Jacobian in its transpose.
    r0 = func(params)
    J = np.zeros((len(params), len(r0)), dtype=np.float64)

    itr = np.nditer(params, flags=['f_index'])
    for _ in itr:
        # TODO: Add central differentiation as alternative.
        step = steps[itr.index]
        params_step = params.copy()
        params_step[itr.index] += step

        r1 = func(params_step)
        J[itr.index, :] = (r1 - r0) / step

    return J.T


def _result(successful: bool, message: str, iterations: int, params: NDArray, error: float) -> Dict[str, Any]:
    return {
        'successful': successful,
        'message': message,
        'iterations': iterations,
        'params': params,
        'error': error
    }
