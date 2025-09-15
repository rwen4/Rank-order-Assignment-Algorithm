  # Rank-Maximal Matching for Resident-Hospital Assignment
  
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
  
  Required packages: PuLP, NumPy, Pandas, Matplotlib, argparse

```pip install pulp numpy pandas matplotlib argparse```
  
  ## Usage
  
  ### Inputting Data
  
  The code takes in two .xlsx files. To run the code, run the following:
  
  ```python rank_matching.py --prefs <path> --caps <path> --out <path>```

  The first xlsx file, prefs, should have two columns: Resident Names/IDs, and their respective preferences, which should be lists separated by commas and ordered in order of preference. 
  
  The second xlsx file, caps, should have two columns: Hospital Names/IDs, and their respective capacities.

  out corresponds to the location where the user wants the output (resident-hospital assignments) to go.
  
  If the paths for prefs or caps is not provided, the user will be prompted for them.

  If the path for out is not provided, it will default to "{pref_path}_results.csv".
  
  ### Example Input Files

  #### prefs.xlsx

  This file should contain each resident’s preferences in **rank order**, separated by commas.

  | Resident | Preferences |
  |----------|-------------|
  | A        | X,Y,Z       |
  | B        | Y,X,Z       |
  | C        | X,Z,Y       |

  - **Resident**: Name or unique ID of the applicant  
  - **Preferences**: A comma-separated list of hospital IDs, ordered from most to least preferred  

  #### caps.xlsx

  This file should contain each hospital and its capacity (number of available slots).

  | Hospital | Capacity |
  |----------|----------|
  | X        | 1        |
  | Y        | 2        |
  | Z        | 1        |

  - **Hospital**: Name or unique ID of the hospital  
  - **Capacity**: Number of residents that hospital can accept  

  
  ### Output
  
  rank_matching.py should output the following
  
  - A status line from PuLP confirming the LP's status result (Final Status: Optimal)
  - Number of Residents Loaded
  - Number of Hospitals Loaded
  - Total matches
  - The number of residents matched for each rank
  
  It will save the resident-hospital assignments to a CSV file, results.csv. 
  
  ## Algorithm Details
  
  ### Problem Description
  
  In order to approach this via Linear Programming, we first define the Rank-Maximal method mathematically:
  
  - Let doctors be indexed by *i ∈ {1, …, N}*  
  - Let hospitals be indexed by *j ∈ {1, …, M}*  
  - Decision variable:  
    - *xᵢⱼ = 1* if doctor *i* is assigned to hospital *j*, 0 otherwise.  
  - Preference indicator:  
    - δ<sub>ij</sub><sup>(r)</sup> = 1 if doctor *i* ranked hospital *j* as rank *r*, 0 otherwise.  
  
  The algorithm proceeds sequentially:  
  1. First, maximize the number of rank-1 matches:  
  
     ![formula](https://latex.codecogs.com/svg.latex?\sum_{j=1}^{M}\sum_{i=1}^{N}x_{ij}\delta_{ij}^{(1)})  
  
     Let this maximum be K₁.  
  
  2. Next, maximize the number of rank-2 matches, subject to the constraint that exactly K₁ rank-1 matches are preserved.  
  
  3. Continue sequentially for higher ranks.  
  
  The final solution is represented by a "rank-maximal signature":  
  [p₁, p₂, …] = [K₁, K₂, …],  
  where each Kᵣ is the number of matches achieved at rank *r*.  
  
  ---
  
  ### Approach (Linear Programming)
  
  The algorithm can be framed as a series of linear programs:
  
  - **Step 1:** Identify all rank-1 preference edges.  
  - **Step 2:** Solve an LP to maximize the number of matches using only those edges.  
  - **Step 3:** Lock those matches and move on to rank-2 edges, adding them as new constraints.  
  
  **Example:**  
  
  | Doctor | Rank 1 | Rank 2 | Rank 3 |
  |--------|--------|--------|--------|
  | A      | X      | Y      | Z      |
  | B      | Y      | X      | Z      |
  | C      | X      | Z      | Y      |
  
  - Rank-1 edges: {(A, X), (B, Y), (C, X)}  
  - Rank-2 edges: {(A, Y), (B, X), (C, Z)}  
  
  Maximization is performed in stages, ensuring earlier rank matches remain fixed as new ranks are considered.  
  
  
  ### Exploitable List Lengths
  
  A challenge arises when doctors rank different numbers of hospitals:
  
  - Doctors may list up to 300 hospitals, but can rank fewer.  
  - This may unfairly reward shorter lists.  
  
  **Example:**  
  - Doctor A: ranks X then Y.  
  - Doctor B: ranks only X.  
  
  If both want X, the algorithm may assign:  
  - X → B (rank 1)  
  - Y → A (rank 2)  
  
  This creates a signature of [1,1], which is “better” than [1,0].  
  As a result, the algorithm incentivizes participants to submit shorter preference lists, which is undesirable.  
  
  **Fix: Dummy Hospital**
  
  To remove this exploit, we introduce a dummy hospital called "None":  
  
  - "None" has infinite capacity.  
  - Any doctor who does not match to a real hospital is automatically matched to "None".  
  - "None" is always treated as the next rank option.  
  
  **Example:**  
  - Doctor A: X, Y  
  - Doctor B: X, None  
  
  Now, if B does not get X, they are matched to "None", which counts as their rank-2 option.  
  
  This ensures fairness:  
  - (A, Y), (B, X)  
  - (A, X), (B, None)  
  are considered equally valid outcomes.  
  
  This modification encourages ranking more hospitals, removing the incentive to submit artificially short lists.  
  
  ## Limitations and Assumptions
  
  Input Size: Complexity grows with the number of edges (resident-hospital preferences). Memory storage requirement may become large if the dataset has many doctors with many preferences, and/or many hospitals. This implementation worked well with a dataset of 300 residents, 100 hospitals, and ranking lists of up to 20 preferences. However, when tested with a life-size dataset of 30,000 residents, 43,000 hospital slots, and ranking lists of up to 300, this implementation was not practically executable.
  
  One-Directional Preferences: We assume in this problem that only the resident has preferences for hospitals. In reality, hospitals also have preferences for residents, which is not considered.
  
  Individual Unfairness: We maximize the number of top-ranked matches overall, however some doctors may be pushed to very low-ranked assignments in order to promote overall satisfaction. 
  
## References

- Irving, R. W., Kavitha, T., Mehlhorn, K., Michail, D., & Paluch, K. E. (2006). *Rank-maximal matchings*. ACM Transactions on Algorithms, 2(4), 602–610. DOI: 10.1145/1198513.1198520. [https://dl.acm.org/doi/pdf/10.1145/1198513.1198520](https://dl.acm.org/doi/pdf/10.1145/1198513.1198520)

- Grötschel, M., Lovász, L., & Schrijver, A. (1981). *The ellipsoid method and its consequences in combinatorial optimization*. Combinatorica, 1(2), 169–197. DOI: 10.1007/BF02579273. [https://link.springer.com/content/pdf/10.1007/BF02579273.pdf](https://link.springer.com/content/pdf/10.1007/BF02579273.pdf)

  
  ## Contributions:
  Richard Wen: rank_matching.py, demo script 
  <br>Jiyi Wang: Establish repository, README
  <br>Jiayou Jiang: Encode the metrics code.
