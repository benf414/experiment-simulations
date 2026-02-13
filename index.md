---
layout: default
title: Comparing Common Experiment Methods
nav_exclude: true
---

# Comparing Common Experiment Methods

## Table of Contents
- [Introduction](#introduction)
- [T-test](#t-test)
- [CUPED](#controlled-experiments-using-pre-experiment-data-cuped)
- [Sequential Tests](#sequential-test)
- [Evaluating the Methods](#evaluating-the-methods)
- [Choosing the Right Method](#choosing-the-right-method)

## Introduction

A/B testing is a core tool for decision-making, helping teams determine whether a change meaningfully impacts users. While the standard t-test is a solid baseline, it can lengthen experiments and struggle to detect changes with small sample sizes. This writeup introduces two widely used alternatives: CUPED and sequential testing. It focuses on practical guidance rather than mathematical derivations to help teams choose the right method based on their goals and constraints.

## T-test

In practical terms, the t-test works by:

1. Comparing outcomes between a group that experiences a change (treatment) and a group that doesn't experience a change (control).
2. Measuring how much the outcomes vary within each group.
3. Estimating how likely the difference measured in Step A can be explained by the natural variance measured in Step B. More natural variation means you could see a larger range of values by chance, so a larger difference in outcomes is required to be considered unlikely.

To make it more intuitive, imagine someone wants to see whether new shoes can help them run faster than their friend. If both normally run between 5:30 and 6:30, it's hard to say whether a 5:45 mile versus their friend's 6:00 mile was caused by the shoes. But if both normally run between 5:55 and 6:05, that same 5:45 versus 6:00 mile provides much stronger evidence that the shoes helped.

## Controlled experiments Using Pre Experiment Data (CUPED)

CUPED is an adjustment that can be applied to an experiment to reduce variance. It recognizes that much of the variation in outcomes is due to baseline differences between units. CUPED works by using pre-experiment data to estimate how much of a unit's outcome can be predicted by it, and then subtracting that predictable component before comparing treatment and control.

Continuing the analogy, imagine two runners whose normal mile times are 5:00 and 10:00. Compared to the average runner, one is consistently faster and one consistently slower. If historical data shows that 80% of their race times can be predicted from their baseline performance, CUPED adjusts each runner's experiment results by removing 80% of their usual deviation from average. In this case, experiment times of 5:00 and 10:00 would be adjusted to 7:00 and 8:00. By accounting for baseline differences, CUPED reduces variance and makes it easier to detect an experiment's effect on the treatment group.

## Sequential Tests

Sequential testing is a method to analyze an experiment multiple times while it is running without increasing the chance of a false positive. A standard t-test assumes the data is only analyzed once at the end. Checking results repeatedly increases the chance of seeing a statistically significant result purely by luck. Sequential testing addresses this by setting multiple checks with higher standards for statistical signficance.

Intuitively, imagine two runners in a 100-meter race. Person A starts strong but stumbles mid-race. Person B temporarily takes the lead, but Person A recovers and ends up winning. If you had paused the race in the moments following Person A's stumble and declared Person B the winner, you would have been wrong. The more often you pause the race, the more likely you would have seen that misleading scenario. Sequential testing accounts for this increased chance by requiring stronger evidence for earlier checks to factor in the amount of time remaining where results could change.

## Evaluating the Methods

The goal of an experiment is to accurately determine whether a tested change has an effect while minimizing the time needed to reach a decision. Compared to standard t-tests, sequential testing aims to shorten experiment duration by allowing early stopping when the observed difference between treatment and control is high. CUPED reduces variance unrelated to the treatment effect, which can improve accuracy in detecting the treatment effect or reduce duration. In this analysis, I focused on duration reduction for both methods as measured by the required sample size to reach a decision.

To compare these methods, I evaluated them using simulated user session data. Each simulation applied a treatment effect ranging from -3% to +3% and measured how they performed. Results also depend on the properties of the outcome metric. I did not evaluate this here, but it is discussed in the next section.

The chart below shows the average required sample size for each method broken out by the treatment effect. CUPED had significantly lower sample sizes. Sequential test totals required slightly more users when the treatment effect was near zero due to stricter standards. However, sample sizes decreased the further the effect was from zero due to early stopping.

![Average Sample Size](visualizations/sample_size_viz.png)

The chart below shows the percent of tests that reached statistical significance broken out by the treatment effect. Despite large decreases in required sample size, test accuracy was similar among all methods.

![Statistical Significance](visualizations/stat_sig_viz.png)

## Choosing the Right Method

### Standard t-test

Pros:
- Simple to implement.
- Easy to interpret.

Cons:
- Checking early invalidates the test.
- Typically requires the largest sample size and duration.

Choose if:
- Staff are unfamiliar with more advanced methods. Effective experimentation requires trust and correct usage. Standard t-tests are the easiest to explain and apply correctly.
- Very large samples are available. Tests often need to run for a minimum amount of time to acount for effectly like novelty, seasonality, and weekly cycles, regardless of whether 20k or 40k users are required.

### T-test with CUPED

Pros:
- Can significantly reduce the required sample size or improve accuracy. However, the effect depends on how well historical data predicts current data.

Cons:
- Moderately more complex to implement.
- Harder to explain. Measurment values are converted and not directly interpretable.
- Checking early invalidates the test.

Choose if:
- Historical data strongly predicts current data. The benefit of CUPED increases with the strength of this relationship.
- Large sample sizes are unavailable. The reduction of variance is useful for small sample sizes where variance can otherwise be too high to detect treatment effects.
- Dedicated data staff are available. While CUPED can significantly reduce variance, it requires careful implementation and validation to maintain good results.

### Sequential test

Pros:
- Easy to interpret.
- Allows results to be checked during the experiment.
- Can significantly reduce required sample size when the treatment effect is large.

Cons:
- Complex to implement.

Choose if:
- Staff are likely to look at results before the experiment ends.
- There is a reasonable expectation that the treatment effect will be large.
- The method is built into your testing software, or dedicated data staff are available to set it up.

### Sequential test with CUPED

Pros:
- Allows results to be checked during the experiment.
- Can drastically reduce the required sample size depending on how well historical data predicts current data, and whether the treatment effect is large.

Cons:
- Complex to implement.
- Harder to explain. Measurment values are converted and not directly interpretable.

Choose if:
- Staff are likely to look at results before the experiment ends.
- Historical data strongly predicts current data, or there is a reasonable expectation of high treatment effect. The impact of CUPED increases with the strength of this relationship.
- Large sample sizes are unavailable. The reduction of variance is useful for small sample sizes where variance can otherwise be too high to detect treatment effects.
- The method is built into your testing software, or dedicated data staff are available to set it up. While CUPED can significantly reduce variance, it requires careful implementation and validation to maintain good results.
