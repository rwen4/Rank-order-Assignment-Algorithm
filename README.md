### Rank-order-Assignment-Algorithm

Prpject desription
This project uses the Rank-Maximal Matching algorithm to assign doctors to hospitals based on their preference lists, and evaluates the quality of the resulting assignments.

Design desicion and motivation：
Why Rank-Maximal Matching: 
Many participants care most about their top choice. The Rank-Maximal Matching algorithm prioritizes satisfying as many first-choice preferences as possible, then second-choice preferences, and so on. This aligns with our core objective: maximize the number of doctors who receive their highest-ranked hospital.

Responsibility for preferences: 
We explicitly design the allocation to respect each doctor's preference list. If two doctors, A and B, both prefer the same hospital and that hospital has only one available slot, we will not favor the doctor who has fewer alternative preferences. For example, if A has additional lower-ranked choices while B does not, we will not automatically assign the slot to B over A. This decision enforces that doctors are accountable for the preferences they submit.

What this repository contains：
An implementation of the Rank-Maximal Matching algorithm tailored for assigning doctors to hospitals with capacity constraints.
Evaluation metrics and scripts to assess assignment quality
The notebook so you can reproduce experiments and tests.

Reference list：
Based on：https://dl.acm.org/doi/pdf/10.1145/1198513.1198520

Contribution：Richard Wen: Encode Match code. Jiyi Wang:Establish repositorie. Jiayou Jiang: Encode the metrics code.
