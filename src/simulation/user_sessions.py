import numpy as np

def user_weekly_session_dist(alpha=3, theta=1):
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

def simulate_users(n_users: int, time_periods: int, sigma=.2, exp_effect=0.0):
    """
    Simulates multiple users over multiple time periods.
    Creates pre-experiment periods for each post-experiment period.
    Starts at initial lambda value then applies random walk with standard deviation sigma.
    Experiment effects are applied to treatment group in post-experiment periods.
    Half of the users are assigned to control and half to treatment.
    """
    if n_users % 2 != 0:
        raise ValueError("n_users must be an even number to split into control and treatment groups")

    pre_c_user_sessions = np.zeros((n_users//2, time_periods), dtype=int)
    post_c_user_sessions = np.zeros((n_users//2, time_periods), dtype=int)
    pre_t_user_sessions = np.zeros((n_users//2, time_periods), dtype=int)
    post_t_user_sessions = np.zeros((n_users//2, time_periods), dtype=int)

    for g in ['control', 'treatment']:
        for i in range(n_users//2):
            lam = user_weekly_session_dist()
            lam_max = lam * 2
            lam_min = min(0, lam * 0.33)
            for t in range(time_periods):
                lam = lam * (1 + np.random.normal(0, sigma))
                lam = max(lam_min, min(lam_max, lam))

                if g == 'control':
                    pre_c_user_sessions[i, t] = user_weekly_sessions(lam)
                else:
                    pre_t_user_sessions[i, t] = user_weekly_sessions(lam)

            if g == 'treatment':
                lam = lam * (1 + exp_effect)
            lam_max = lam * 2
            lam_min = min(0, lam * 0.33)
            
            for t in range(time_periods):
                lam = lam * (1 + np.random.normal(0, sigma))
                lam = max(lam_min, min(lam_max, lam))

                if g == 'control':
                    post_c_user_sessions[i, t] = user_weekly_sessions(lam)
                else:
                    post_t_user_sessions[i, t] = user_weekly_sessions(lam)
    
    return pre_c_user_sessions, post_c_user_sessions, pre_t_user_sessions, post_t_user_sessions