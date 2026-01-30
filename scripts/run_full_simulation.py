import sys

from datetime import datetime

sys.path.append('../src')
from evaluation.evaluate_experiments import evaluate_experiments, summarize_results
from evaluation.visualize_experiments import create_viz_stat_sig, create_viz_sample_size

def run_full_simulation(
        n_pop_per_test=100000,
        mde=.015,
        cuped_ss_adj=.1,
        n_tests_per_effect=100,
        effect_start=-.03,
        effect_end=.031,
        effect_step=.005,
        write_output=True
):
    """
    Evaluates experiment data.

    Args:
        n_pop_per_test: population of users which each test will sample from
        cuped_ss_adj: percent adjustment on CUPED required sample size
        mde: minimum detectable effect per test
        n_tests_per_effect: number of tests per effect size
        effect_start: starting effect size
        effect_end: ending effect size (exclusive)
        effect_step: step size for effect sizes
        write_output: whether to write output to Data folder
    """
    print(f'Simulation started at {datetime.now().strftime("%H%M%S")}')

    results = evaluate_experiments(
        n_pop_per_test=n_pop_per_test,
        mde=mde,
        cuped_ss_adj=cuped_ss_adj,
        n_tests_per_effect=n_tests_per_effect,
        effect_start=effect_start,
        effect_end=effect_end,
        effect_step=effect_step
    )
    summarized_results = summarize_results(results)

    fig = create_viz_stat_sig(summarized_results)
    fig2 = create_viz_sample_size(summarized_results)

    if write_output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results.to_csv(f'data/results_{timestamp}.csv', index=False)
        summarized_results.to_csv(f'data/summarized_results_{timestamp}.csv', index=False)
        fig.savefig(f'data/stat_sig_viz_{timestamp}.png')
        fig2.savefig(f'data/sample_size_viz_{timestamp}.png')

    print(f'Simulation completed at {datetime.now().strftime("%H%M%S")}')