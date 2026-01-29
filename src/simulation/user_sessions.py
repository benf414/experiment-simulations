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
    Mean value is lam.
    Active users must have a session so value is 1 + poisson value.
    """
    sessions = np.random.poisson(lam)
    return sessions

def simulate_users(n_users: int, time_periods: int, exp_effect=0.0):
    """
    Simulates multiple users over multiple time periods.
    Adds an experimental effect to the treatment group in the post-experiment period.
    Half of the users are assigned to control and half to treatment.
    Half of the time periods are considered pre-experiment and half post-experiment.
    Returns 4 arrays of shape (n_users, time_periods/2) with the number of sessions for each user in each time period.
    """
    if n_users % 2 != 0:
        raise ValueError("n_users must be an even number to split into control and treatment groups")
    if time_periods % 2 != 0:
        raise ValueError("time_periods must be an even number to split into pre and post experiment periods")

    pre_c_user_sessions = np.zeros((n_users//2, time_periods//2), dtype=int)
    post_c_user_sessions = np.zeros((n_users//2, time_periods//2), dtype=int)
    pre_t_user_sessions = np.zeros((n_users//2, time_periods//2), dtype=int)
    post_t_user_sessions = np.zeros((n_users//2, time_periods//2), dtype=int)

    for i in range(n_users//2):
        lam = user_weekly_session_dist()
        lam_affected = user_weekly_session_dist(theta=1*(1+exp_effect))
        for t in range(time_periods//2):
            pre_c_user_sessions[i, t] = user_weekly_sessions(lam)
            post_c_user_sessions[i, t] = user_weekly_sessions(lam)
            pre_t_user_sessions[i, t] = user_weekly_sessions(lam)
            post_t_user_sessions[i, t] = user_weekly_sessions(lam_affected)
    
    return pre_c_user_sessions, post_c_user_sessions, pre_t_user_sessions, post_t_user_sessions