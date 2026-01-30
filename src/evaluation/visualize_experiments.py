import matplotlib.pylab as plt
import seaborn as sns

def create_viz_stat_sig(summarized_results):
    """
    Creates visualization of statistical significance per test per true treatment effect
    """
    fig, ax = plt.subplots()
    sns.lineplot(data=summarized_results, x='true_effect', y='significance', hue='test_lbl', ax=ax)
    ax.set_title('Percent Statistical Significance by Test')
    ax.set_xlabel('True Effect')
    ax.xaxis.set_major_formatter(plt.FuncFormatter('{0:.1%}'.format))
    ax.set_ylim(bottom=0)
    ax.set_ylabel('Stat Sig')
    ax.yaxis.set_major_formatter(plt.FuncFormatter('{0:.0%}'.format))
    ax.legend(title=None)

    return fig

def create_viz_sample_size(summarized_results):
    """
    Creates visualization of average sample size per test per true treatment effect
    """
    fig, ax = plt.subplots()
    ax = sns.lineplot(data=summarized_results, x='true_effect', y='sample_size', hue='test_lbl')
    ax.set_title('Average Sample Size by Test')
    ax.set_xlabel('True Effect')
    ax.xaxis.set_major_formatter(plt.FuncFormatter('{0:.1%}'.format))
    ax.set_ylim(bottom=0)
    ax.set_ylabel('Sample Size')
    ax.legend(title=None)

    return fig