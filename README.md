# Rank-order-Assignment-Algorithm

## Project Description

This project assigns doctors to hospitals based on their preference lists by making use of the Rank-Maximal Matching algorithm, a method for assigning applicants to positions in a way that maximizes satisfaction based on preference rankings. This method aims to produce a matching that favors as many first-choice assignments as possible, then second-choice assignments, and so on. 

## Background & Motivation

The challenge of the Resident-Hospital matching problem is to design an assignment that is fair and efficient. 
The Rank-Maximal Matching approaches this challenge by prioritizing the maximization of high-preference assignments in a hierarchical fashion:

1. First, it maximizes the number of first-choice matches
2. With first-choice matches constant at maximum, maximize second-choice matches
3. Continue for all ranks

By maximizing first-choice matches before considering lower-ranked options, the Rank-Maximal method maximizes overall satisfaction over individual guarantees. It places as many people as possible into their top preferences even if a few participants may end up with less favorable outcomes than they could have gotten. 

## Installation/Requirements

Python v.3.13.7

Required packages: PuLP, NumPY, Pandas, MatPlotLib, argparse

## Usage

### Inputting Data

The code takes in two .xlsx files. To run the code, run the following:

```python rank_matching.py --prefs <path> --caps <path>```

The first one, prefs, should have two columns: Resident Names/IDs, and their respective preferences, which should be lists separated by commas and ordered in order of preference. 

The second one, caps, should have two columns: Hospital Names/IDs, and their respective capacities.

See Demo script for example datasets.

### Output

rank_matching.py should output the following

- A status line from PuLP confirming the LP's status result (Final Status: Optimal)
- Number of Residents Loaded
- Number of Hospitals Loaded
- Total matches
- The number of residents matched for each rank
- A preview of the first 15 assignments

It will save the resident-hospital assignments to a CSV file, results.csv. 

### Responsibility for preferences: 

We explicitly design the allocation to respect each doctor's preference list. If two doctors, A and B, both prefer the same hospital and that hospital has only one available slot, we will not favor the doctor who has fewer alternative preferences. For example, if A has additional lower-ranked choices while B does not, we will not automatically assign the slot to B over A. This decision enforces that doctors are accountable for the preferences they submit.


## Reference list：
Based on：https://dl.acm.org/doi/pdf/10.1145/1198513.1198520

Contribution：Richard Wen: Encode Match code. Jiyi Wang:Establish repositorie. Jiayou Jiang: Encode the metrics code.
