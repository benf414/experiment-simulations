import numpy as np
import pandas as pd

from simulation.user_sessions import simulate_users
from experiments.pre_test_analysis import required_sample_size, estimate_cuped_stats
from experiments.experiment import experiment

def evaluate_experiments(
        n_pop_per_test=100000,
        n_periods_per_test=4,
        mde=.015,
        cuped_ss_adj=.1,
        n_tests_per_effect=100,
        effect_start=-.03,
        effect_end=.031,
        effect_step=.005
):
    """
    Evaluates experiment data.

    Args:
        n_pop_per_test: population of users which each test will sample from
        n_periods_per_test: number of time periods per test
        mde: minimum detectable effect per test
        cuped_ss_adj: percent adjustment on CUPED required sample size
        n_tests_per_effect: number of tests per effect size
        effect_start: starting effect size
        effect_end: ending effect size (exclusive)
        effect_step: step size for effect sizes
    """

    cuped_corrcoef, cuped_theta = estimate_cuped_stats(10000, n_periods_per_test)
    results = pd.DataFrame()

    for _ in range(n_tests_per_effect):
        for te in np.arange(effect_start, effect_end, effect_step):
            te_adj = round(te.item(), 3)
            pre_c_users, post_c_users, pre_t_users, post_t_users = simulate_users(n_pop_per_test, n_periods_per_test, exp_effect=te_adj)
            pre_exp_users_sum = np.vstack([pre_c_users, pre_t_users]).sum(axis=1)
            t_test_n, t_test_cuped_n, seq_test_n, seq_test_cuped_n = required_sample_size(pre_exp_users_sum, cuped_corr_coef=cuped_corrcoef, mde=mde)

            exp = experiment(
                pre_c_user_sessions=pre_c_users,
                post_c_user_sessions=post_c_users,
                pre_t_user_sessions=pre_t_users,
                post_t_user_sessions=post_t_users,
                t_test_n=t_test_n,
                t_test_cuped_n=round(t_test_cuped_n * (1 + cuped_ss_adj)),
                seq_test_n=seq_test_n,
                seq_test_cuped_n=round(seq_test_cuped_n * (1 + cuped_ss_adj)),
                cuped_theta=cuped_theta
            )
            exp.create_test_groups()
            exp.create_test_entries()
            exp.create_test_entry_data()
            exp.run_experiment()

            results = pd.concat([results, pd.DataFrame([{
                'test': 'ttest',
                'true_effect': te_adj,
                'p_value': exp.results['ttest']['p_value'],
                'significance': exp.results['ttest']['significance'],
                'true_pos': 1 if exp.results['ttest']['p_value'] < .05 and te_adj != 0 else 0,
                'false_pos': 1 if exp.results['ttest']['p_value'] < .05 and te_adj == 0 else 0,
                'true_neg': 1 if exp.results['ttest']['p_value'] >= .05 and te_adj == 0 else 0,
                'false_neg': 1 if exp.results['ttest']['p_value'] >= .05 and te_adj != 0 else 0,
                'sample_size': exp.results['ttest']['sample_size']
            }])], ignore_index=True)

            results = pd.concat([results, pd.DataFrame([{
                'test': 'ttest_cuped',
                'true_effect': te_adj,
                'p_value': exp.results['ttest_cuped']['p_value'],
                'significance': exp.results['ttest_cuped']['significance'],
                'true_pos': 1 if exp.results['ttest_cuped']['p_value'] < .05 and te_adj != 0 else 0,
                'false_pos': 1 if exp.results['ttest_cuped']['p_value'] < .05 and te_adj == 0 else 0,
                'true_neg': 1 if exp.results['ttest_cuped']['p_value'] >= .05 and te_adj == 0 else 0,
                'false_neg': 1 if exp.results['ttest_cuped']['p_value'] >= .05 and te_adj != 0 else 0,
                'sample_size': exp.results['ttest_cuped']['sample_size']
            }])], ignore_index=True)

            results = pd.concat([results, pd.DataFrame([{
                'test': 'seq',
                'true_effect': te_adj,
                'p_value': exp.results['seq']['p_value'],
                'significance': exp.results['seq']['significance'],
                'true_pos': 1 if exp.results['seq']['p_value'] < .05 and te_adj != 0 else 0,
                'false_pos': 1 if exp.results['seq']['p_value'] < .05 and te_adj == 0 else 0,
                'true_neg': 1 if exp.results['seq']['p_value'] >= .05 and te_adj == 0 else 0,
                'false_neg': 1 if exp.results['seq']['p_value'] >= .05 and te_adj != 0 else 0,
                'sample_size': exp.results['seq']['sample_size']
            }])], ignore_index=True)

            results = pd.concat([results, pd.DataFrame([{
                'test': 'seq_cuped',
                'true_effect': te_adj,
                'p_value': exp.results['seq_cuped']['p_value'],
                'significance': exp.results['seq_cuped']['significance'],
                'true_pos': 1 if exp.results['seq_cuped']['p_value'] < .05 and te_adj != 0 else 0,
                'false_pos': 1 if exp.results['seq_cuped']['p_value'] < .05 and te_adj == 0 else 0,
                'true_neg': 1 if exp.results['seq_cuped']['p_value'] >= .05 and te_adj == 0 else 0,
                'false_neg': 1 if exp.results['seq_cuped']['p_value'] >= .05 and te_adj != 0 else 0,
                'sample_size': exp.results['seq_cuped']['sample_size']
            }])], ignore_index=True)

    return results

def summarize_results(results):
    """
    Summarizes results dataframe for evaluation
    """
    rates = results.groupby(['test', 'true_effect'])[['sample_size', 'p_value', 'significance', 'true_pos', 'false_pos', 'true_neg', 'false_neg']].mean().reset_index()
    rates['alpha'] = rates['false_pos'] / (rates['false_pos'] + rates['true_neg'])
    rates['power'] = rates['true_pos'] / (rates['true_pos'] + rates['false_neg'])
    rates[['alpha', 'power']] = rates[['alpha', 'power']].fillna(0)

    test_order = ["T", "T (CUPED)", "Sequential", "Sequential (CUPED)"]
    test_col = {
        "ttest": test_order[0],
        "ttest_cuped": test_order[1],
        "seq": test_order[2],
        "seq_cuped": test_order[3]
    }
    rates['test_lbl'] = rates['test'].map(test_col)
    rates['test_lbl'] = pd.Categorical(rates['test_lbl'], categories=test_order, ordered=True)

    return rates