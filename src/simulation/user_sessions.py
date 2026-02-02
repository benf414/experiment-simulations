import math
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
    Half of the users are assigned to control and half to treatment.
    Creates pre-experiment periods for each post-experiment period.
    Experiment effects are applied equally to all units in the treatment group during post-experiment periods.
    Starts at initial lambda value then applies Geometric Brownian motion to simulate change over time.
    Based on sigma 68% of steps are within x of the starting value: .1 -> (91%,111%), .2 -> (82%,122%), .3 -> (74%,135%)
    Based on sigma 95% of steps are within x of the starting value: .1 -> (82%,122%), .2 -> (67%,149%), .3 -> (55%,182%)
    Reflections are placed at 50% and 200% of the starting value calculated separately for pre and post experiment periods.
    """
    if n_users % 2 != 0:
        raise ValueError("n_users must be an even number to split into control and treatment groups")

    pre_c_user_sessions = np.zeros((n_users//2, time_periods), dtype=int)
    post_c_user_sessions = np.zeros((n_users//2, time_periods), dtype=int)
    pre_t_user_sessions = np.zeros((n_users//2, time_periods), dtype=int)
    post_t_user_sessions = np.zeros((n_users//2, time_periods), dtype=int)

    mu = -.5 * sigma**2  #ensure no drift

    for g in ['control', 'treatment']:
        for i in range(n_users//2):
            lam = user_weekly_session_dist()
            log_lam = math.log(lam)
            log_lam_min = log_lam - .693
            log_lam_max = log_lam + .693
            
            for t in range(time_periods):
                log_lam += max(min(np.random.normal(mu, sigma), 1.4), -1.4) #avoid steps larger than distance between min/max
                if log_lam < log_lam_min:
                    log_lam = log_lam_min + (log_lam_min - log_lam)
                elif log_lam > log_lam_max:
                    log_lam = log_lam_max - (log_lam - log_lam_max)
                lam = math.exp(log_lam)

                if g == 'control':
                    pre_c_user_sessions[i, t] = user_weekly_sessions(lam)
                else:
                    pre_t_user_sessions[i, t] = user_weekly_sessions(lam)

            if g == 'treatment':
                lam = lam * (1 + exp_effect)
            
            log_lam = math.log(lam)
            log_lam_min = log_lam - .693
            log_lam_max = log_lam + .693
            
            for t in range(time_periods):
                log_lam += max(min(np.random.normal(mu, sigma), 1.4), -1.4) #avoid steps larger than distance between min/max
                if log_lam < log_lam_min:
                    log_lam = log_lam_min + (log_lam_min - log_lam)
                elif log_lam > log_lam_max:
                    log_lam = log_lam_max - (log_lam - log_lam_max)
                lam = math.exp(log_lam)

                if g == 'control':
                    post_c_user_sessions[i, t] = user_weekly_sessions(lam)
                else:
                    post_t_user_sessions[i, t] = user_weekly_sessions(lam)
    
    return pre_c_user_sessions, post_c_user_sessions, pre_t_user_sessions, post_t_user_sessions