# Comparing Common Experiment Methods

A/B testing is a core tool for decision-making, helping teams determine whether a change meaningfully impacts users. While the standard t-test is simple and effective, it can be inefficient in product experiments. The writeup [here](https://benf414.github.io/experiment-simulations/) introduces and evaluates two widely used alternatives: CUPED and sequential testing. It also provides guidance on choosing the method based on a team's goals and constraints.

## How to Run

Executing the below script will run the simulation and save test output and visualizations to the directory's data folder

```
python scripts/run_full_simulation.py
```

## Methodology

### User Data

User data was created as 1 week session totals. A gamma distribution ($\alpha = 3, \theta = 1$) is used to create the original poisson distribution $\lambda$. This creates a longer tail than using poisson ($\lambda = 3$). I this this better models the wider range of activity between different users, such as the existence of power users.

A simple multiplicative random walk is added to the following weeks' poisson $\lambda$ for each user. It adds a percent change equal to a sample from a normal distribution ($\sigma = .2$). Minimum global change is capped at -66% and maximum global change at 100%. This model is not as accurate as more involved options, but it's sufficient for the purposes here and shouldn't lead to significant issues with analysis.

### Test Methods

The test methods were t-test, t-test with CUPED, sequential test, sequential test with CUPED. Power analysis was conducted using $\alpha = .05$, power = .8, and minimum detectable effect = .015 measured as percent change from mean. 10% was added to CUPED sample sizes to account for the larger estimate in variance compared to tests without it. 

The CUPED adjustment was done via an estimated $\theta$ using historical data rather than using experiment data because A) Treatment effects are heterogenous so including treatment in the covariance creates issues; and B) Re-calculating $\theta$ during each look in sequential testing will increase the false positive rate.

The CUPED correlation coefficient was estimated ~.75 between pre- and post-experiment sessions totaled over 4 weeks. That seems reasonable and creates a 56% decrease in variance. $\theta$ was estimated ~.9.

Boundaries for sequential testing was done via the O'Brien-Flemming method. Over 4 looks of 1 week each, it requires p-values under .001, .0039, .0185, and .045 respectiely to reach statistical significance.

### Evaluation

100 of each test method were run at each true treatment effect between -3% and 3% at .5% intervals. Statistical power, Type I error rate, and average sample size were used to evaluate the methods.
