# Rank-order-Assignment-Algorithm

## Prpject desription

This project uses the Rank-Maximal Matching algorithm to assign doctors to hospitals based on their preference lists, and evaluates the quality of the resulting assignments.

## Design desicion and motivation：
### Why Rank-Maximal Matching: 

Many participants care most about their top choice. The Rank-Maximal Matching algorithm prioritizes satisfying as many first-choice preferences as possible, then second-choice preferences, and so on. This aligns with our core objective: maximize the number of doctors who receive their highest-ranked hospital.

### Responsibility for preferences: 

We explicitly design the allocation to respect each doctor's preference list. If two doctors, A and B, both prefer the same hospital and that hospital has only one available slot, we will not favor the doctor who has fewer alternative preferences. For example, if A has additional lower-ranked choices while B does not, we will not automatically assign the slot to B over A. This decision enforces that doctors are accountable for the preferences they submit.


## Implementation Choices

We decided to implement the Rank-Maximal Matching algorithm using a linear programming method. We achieve this with the usage of the PuLP package (see documentation here: https://coin-or.github.io/pulp/)

### Algorithm

The algorithm optimizes the rank matching by lexicographically maximizing (maximizing from left to right) the vector r where
$ r = [r_1, r_2, r_3, r_4...] $
Where r_n represents the number of rank-n matches made.

In order to implement this with linear programming, we do the following:
1. First we maximize r_1 by building a linear program and finding the maximum possible number of rank-1 matches.
3. We assign the maximum number of rank-1 matches obtained previously to a variable, K_1.
4. We add a constraint to the linear program that r[1] == K_1, then maximize r_2 with this linear program.
5. We assign the maximum r_2 to K_2, and add additional constraint r[2] == K_2.
6. Repeat for all ranks in r.

### Explanation of Choices Made in Implementation

After we take in the list of hospitals with their capacities, we append a dummy hospital "None" with excess (len(residents)+1) capacity. 
We then append this dummy hospital at the very end of each resident's preference list. 

The number of hospitals that a resident ranks is variable. Residents can rank up to 20, but can rank less. 
Since the algorithm will prioritize giving all residents matches, residents that have shorter ranking lists have an unfair advantage.

For instance, consider the following residents and their preference lists. For the sake of simplicity, assume all hospitals have a max capacity of 1.

<div class="alert alert-block alert-info">
<b>Dr. X:</b> 
    <br>1. Hospital A
    <br>2. Hospital B

<br>
</div>
<div class="alert alert-block alert-info">
<b>Dr. Y:</b> 
    <br>1. Hospital A 
</div>


By default, the algorithm will find that the maximum number of rank-1 matches will be 1, since both residents selected Hospital A as their rank 1 choice. However, once it finds the maximum of rank-1 matches, it will go on to find a maximum number of rank-2 matches. 

Since Dr. Y did not select any hospital as their rank 2 option, there is only one possible configuration where the rank 1 matches are at their maximum (1) and rank 2 matches are at their maximum (1), [(Dr. X, Hospital B),(Dr. Y, Hospital A)].

This gives an unfair advantage to Dr. Y as they got a higher ranked choice simply due to the fact that they chose to rank less schools.

By appending a dummy hospital "None" with excess capacity to each list and treating it as their next-ranked option:

<div class="alert alert-block alert-info">
<b>Dr. X:</b> 
    <br>1. Hospital A
    <br>2. Hospital B
    <br>3. None <<<<<<

<br>
</div>
<div class="alert alert-block alert-info">
<b>Dr. Y:</b> 
    <br>1. Hospital A 
    <br>2. None <<<<<<
</div>
There are now 2 different configurations with 1 rank-1 match and 1 rank-2 match:
[(Dr. X, Hospital B),(Dr. Y, Hospital A)] and [(Dr. X, Hospital A),(Dr. Y, None)]

In this scenario, the algorithm will choose either of these configurations equally. 
Unfortunately, this results in Dr. Y being unranked. However, we decided that in this scenario, punishing shorter lists is preferable over rewarding shorter lists.

This may change when applied to the actual match system, where residents can pay to lengthen their lists to 300. 


## Reference list：
Based on：https://dl.acm.org/doi/pdf/10.1145/1198513.1198520

Contributions：
Richard Wen: Algorithm Script
Jiyi Wang: Establish repository and documentation
Jiayou Jiang: Evaluation and Metrics Scripts
