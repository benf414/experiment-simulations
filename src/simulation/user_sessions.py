import numpy as np

def user_weekly_session_dist(alpha=2.5, theta=1):
    """
    Samples from a gamma distribution to find the poisson lambda parameter.
    Mean value is alpha * theta.
    """
    gamma_value = np.random.gamma(alpha, theta)
    return gamma_value

def user_weekly_sessions(lam: float):
    """
    Simulates a single user's weekly sessions via a poisson distribution.
    Mean poisson value is lam.
    Active users must have a session so value is 1 + poisson value.
    """
    sessions = 1 + np.random.poisson(lam)
    return sessions
