import numpy as np

from scipy.stats import norm
from simulation.user_sessions import simulate_users

def cuped_corr_coef(n_users: int, time_periods: int):
	"""
    Calculate CUPED correlation coefficients by comparing multiple simulated pre-experiment time periods
    
	Args:
		n_users: number of users in population
		time_periods: number of time periods where half are assigned to each group
    """
	pre_users1, post_users1, pre_users2, post_users2 = simulate_users(n_users, time_periods)
	pre_users_sum = np.vstack([pre_users1, pre_users2]).sum(axis=1)
	post_users_sum = np.vstack([post_users1, post_users2]).sum(axis=1)
	
	cuped_corr_coef = np.corrcoef(pre_users_sum.flatten(), post_users_sum.flatten())[0, 1]
	return cuped_corr_coef

def required_sample_size(population_data, alpha=.05, power=.8, mde=.02, cuped_corr_coef=0.0, seq_final_alpha=.05):
	"""
	Calculate required sample size for a t-test, t-test with CUPED, group sequential test, and group sequential test with CUPED.

	Args:
		population_data (array): the pre-experiment population data.
		alpha: chance of false positive.
		power: chance of detecting an effect if there is one.
		mde: minimum effect size to detect measured as a percent difference from mean.
		cuped_corr_coef: correlation coefficient for CUPED adjustment.
		seq_final_alpha: final alpha for the group sequential test.
	Returns:
		float: Required sample size per group for a t-test.
		float: Required sample size per group for a t-test with CUPED adjustment.
		float: Required sample size per group for a group sequential test.
		float: Required sample size per group for a group sequential test with CUPED adjustment.
	"""
	mean = np.mean(population_data)
	stddev = np.std(population_data, ddof=1)
	z_alpha = norm.ppf(1 - alpha/2)
	seq_alpha = norm.ppf(1 - seq_final_alpha/2)
	z_power = norm.ppf(power)
	t_test_n = 2 * (z_alpha + z_power)**2 * stddev**2 / (mde * mean)**2
	seq_test_n = 2 * (seq_alpha + z_power)**2 * stddev**2 / (mde * mean)**2
	t_test_cuped_n = t_test_n * (1 - cuped_corr_coef**2)
	seq_test_cuped_n = seq_test_n * (1 - cuped_corr_coef**2)
	return round(t_test_n), round(t_test_cuped_n), round(seq_test_n), round(seq_test_cuped_n)