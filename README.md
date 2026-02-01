# Comparing Common Experiment Methods

A/B testing is a core tool for decision-making, helping teams determine whether a change meaningfully impacts users. While the standard t-test is a solid baseline, it can require longer experiments and struggle to detect changes with small sample sizes. The writeup [here](https://benf414.github.io/experiment-simulations/) introduces two widely used alternatives: CUPED and sequential testing. It focuses on practical guidance rather than mathematical derivations to help teams choose the right method based on their goals and constraints.

## How to Run

Executing the below script will run the simulation and save test output and visualizations to the directory's data folder

```
python scripts/run_full_simulation.py
```

| Argument | Default | Description
| -------- | ------- | -----------
| n_pop_per_test | 100000 | number of users in population which each test will sample from
| mde | .015 | minimum detectable effect for sample size requirements as measured by percent of population mean
| cuped_ss_adj | .1 | percent adjustment on CUPED tests' required sample size
| n_tests_per_effect | 100 | number of tests to simulate per treatment effect
| effect_start | -.03 | bottom range of treatment effects to simulate
| effect_end | .031 | top range of treatment effects to simulate (exclusive)
| effect_step | .005 | intervals within the effect range to simulate
| write_output | True | whether to write output to the Data folder

## Methodology

### User Data

User data was created as 1 week session totals. A gamma distribution ($\alpha = 3, \theta = 1$) is used to create the original poisson distribution $\lambda$. This creates a longer tail than using poisson ($\lambda = 3$). I think this better models the wider range of activity between different users, such as the existence of power users.

A simple multiplicative random walk is added to the following weeks' poisson $\lambda$ for each user. It adds a percent change equal to a sample from a normal distribution ($\sigma = .2$). Minimum global change is capped at -66% and maximum global change at 100%. This model is not as fine-tuned as more involved options, but it's sufficient for the purposes here and shouldn't lead to significant issues with analysis.

### Test Methods

The test methods were t-test, t-test with CUPED, sequential test, sequential test with CUPED.

The t-test required sample size is $n = \frac{2 * (Z_{1 - \alpha/2} + Z_{1 - \beta})^2 * \sigma^2}{MDE^2}$ where $Z_{1 - \alpha/2}$ is the Z-distribution value based on desired chance of statistical significance given no true treatment effect ($\alpha$), $Z_{1 - \beta}$ is the Z-distribution value based on desired chance of statistical significance given a true treatment effect ($1 - \beta$), $\sigma$ is the population standard deviation, and $MDE$ is the desired minimum detectable effect. Calculations used $\alpha$ = .05, $\beta$ = .2, and $MDE$ = .015 * population mean ($\mu$). Sequential tests used the final look's $\alpha$ = .045. An extra 10% was added to CUPED sample sizes to account for the larger estimate in variance compared to tests without it.

The CUPED adjustment is $Y_i^{CUPED} = Y_i - \theta * (X_i - \bar{X})$ where $Y_i$ is the original value, $\theta$ is the covariance of pre-experiment data $X$ and post-experiment data $Y$ divided by the variance of pre-experiment data, $X_i$ is the pre-experiment value, and $\bar{X}$ is the pre-experiment population mean. $\theta$ was calculated using historical data rather than using experiment data because re-calculating during each look in sequential testing can increase the false positive rate. $\rho$ was estimated ~ .75 comparing 4 week session totals, creating a ~56% decrease in variance. $\theta$ was estimated ~ .9.

Boundaries for sequential testing were determined via the O'Brien-Flemming method. Over 4 looks of equal information, it requires p-values under .0001, .0039, .0185, and .045 respectiely to reach statistical significance.

### Evaluation

100 of each test method were run at each true treatment effect between -3% and 3% at .5% intervals. Statistical power, Type I error rate, and average sample size were used to evaluate the methods.
