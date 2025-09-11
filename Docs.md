
# Rank‑Maximal Residency Matching with PuLP

This project demonstrates how to compute a rank‑maximal matching between residents and hospitals using Linear Programming (LP) with PuLP. It:

- Generates synthetic preference data and hospital capacities
- Formulates and solves a rank‑maximal assignment model (maximize #1 choices first, then #2, etc.)
- Produces a concrete matching plus a “signature” that reports how many residents received each preference rank
- Evaluates and visualizes outcomes (first‑choice rate, weighted score, average rank, histogram)

The notebook is self‑contained: you can generate data, solve the LP, and evaluate results in one place.

---

## Contents

- [What is rank‑maximal matching?](#what-is-rank-maximal-matching)
- [Project structure and workflow](#project-structure-and-workflow)
- [Input data formats](#input-data-formats)
- [How it works (LP formulation)](#how-it-works-lp-formulation)
- [Why we add a “None” hospital](#why-we-add-a-none-hospital)
- [Quick start](#quick-start)
- [Configuration and customization](#configuration-and-customization)
- [Outputs and interpretation](#outputs-and-interpretation)
- [Evaluation metrics and plots](#evaluation-metrics-and-plots)

---

## What is rank‑maximal matching?

Given:
- A set of residents with ordered lists of preferred hospitals
- Hospitals with capacities

We seek an assignment of residents to hospitals (respecting capacities) that is as favorable as possible to residents’ top choices, lexicographically:
1. Maximize the number of first‑choice matches
2. Subject to (1), maximize the number of second‑choice matches
3. Subject to (1) and (2), maximize the number of third‑choice matches
4. … and so on

This lexicographic optimization is commonly called a rank‑maximal matching.

---

## Project structure and workflow

The Jupyter notebook performs the following steps:

1. Generate synthetic data:
   - Residents: IDs `0001` → `0300`
   - Hospitals: IDs `9001` → `9330`
   - Each resident ranks 10–20 hospitals at random
   - All hospitals default to capacity 1 (configurable)

2. Save inputs (for transparency and reuse):
   - `residents_prefs.xlsx` with two columns: `Names`, `Preferences`
   - `hospital_capacities.xlsx` with two columns: `Hospital`, `Capacity`

3. Normalize and prepare:
   - Zero‑pad IDs to 4 digits
   - Filter invalid IDs
   - Append a dummy hospital `"None"` with large capacity to neutralize “short list” advantages (see below)

4. Build and solve the LP:
   - Decision variables \(x_{ij} \in [0,1]\) indicate whether resident \(i\) is assigned to hospital \(j\)
   - Capacity and “at‑most‑one” constraints
   - Lexicographic objective via sequential “lock‑in” of optimal totals

5. Extract results and artifacts:
   - Matching list
   - Rank‑maximal signature (# matched at rank 1, rank 2, ...)
   - CSVs for evaluation: `preferences.csv`, `assignments.csv`

6. Evaluate and visualize:
   - Compute first‑choice rate, weighted score, average rank
   - Plot histogram of assigned ranks (with an “Unmatched” bucket when used in other settings)

---

## Input data formats

You can use the generated Excel files or provide your own data in the same format.

- `residents_prefs.xlsx`
  - `Names`: resident ID (string). Example: `0001`
  - `Preferences`: comma‑separated hospital IDs (strings), ordered by preference. Example: `9058,9013,9141,...`

- `hospital_capacities.xlsx`
  - `Hospital`: hospital ID (string). Example: `9001`
  - `Capacity`: integer capacity (non‑negative)

Notes:
- IDs are normalized to 4‑digit strings (`zfill(4)`).
- The code filters out any hospital IDs not listed in `hospital_capacities.xlsx`.

---

## How it works (LP formulation)

Let:
- \( I \) be residents
- \( J \) be hospitals
- \( r_{ij} \in \{1,2,\dots\} \) be the rank of hospital \( j \) in resident \( i \)’s list (lower is better)
- \( \text{cap}_j \) be the capacity of hospital \( j \)

Decision variables:
- \( x_{ij} \in \{0,1\} \) — whether resident \( i \) is assigned to hospital \( j \)

Constraints:
- Each resident is assigned to at most one hospital:
  \[
  \forall i \in I: \sum_{j \in J} x_{ij} \le 1
  \]
- Hospital capacity:
  \[
  \forall j \in J: \sum_{i \in I} x_{ij} \le \text{cap}_j
  \]

Rank‑maximal objective via staged optimization:

1) Maximize total matches:
\[
\max \sum_{i \in I}\sum_{j \in J} x_{ij}
\]
Let \(K_{\text{total}}\) be the optimum. Lock it:
\[
\sum_{i,j} x_{ij} = K_{\text{total}}
\]

2) For rank \(r = 1,2,\dots,R\), maximize the number of rank‑\(r\) matches subject to previous locks:
\[
\max \sum_{(i,j): r_{ij} = r} x_{ij}
\]
Denote the optimum \(K_r\) and lock it:
\[
\sum_{(i,j): r_{ij} = r} x_{ij} = K_r
\]

This yields a lexicographically optimal vector \((K_1, K_2, \dots, K_R)\).

Implementation details:
- The notebook uses continuous variables in \([0,1]\). Due to the problem’s structure (a network flow polytope), optimal solutions are integral. You can switch to `cat="Binary"` if preferred.

---

## Why we add a “None” hospital

Residents can submit lists of varying lengths (10–20 in the demo). Without care, residents who rank fewer hospitals can gain an unfair advantage in the lexicographic optimization. To neutralize this, we append a dummy hospital `"None"` to every resident’s list with excess capacity.

Effectively, each resident has one more, least‑preferred option. This prevents short lists from inflating second‑choice counts, ensuring fair comparison across different list lengths. In real deployments, you may replace `"None"` with “Unassigned” or configure minimum list lengths.

The notebook includes a detailed example explaining this effect.

---

## Quick start

Prerequisites:
- Python 3.9+ (tested with 3.13)
- CBC solver via PuLP (default in most environments)

Install dependencies:
```bash
pip install pulp pandas numpy matplotlib openpyxl
```

Run the notebook:
1. Open `Demo.ipynb` in Jupyter or VS Code.
2. Run cells from top to bottom.
3. Observe generated files and printed results.

Expected (sample) console output:
```
# residents: 300
# hospitals: 331
Locked total matches: 300
Rank-maximal signature (count per rank):
  rank 1: 195
  rank 2: 56
  rank 3: 17
  rank 4: 11
  rank 5: 7
  rank 6: 5
  rank 7: 1
  rank 8: 3
  rank 9: 1
  rank 10: 1
  rank 11: 1
  rank 12: 0
  rank 13: 0
  rank 14: 1
  rank 15: 0
  rank 16: 1
  ...
# matched pairs in solution: 300
```

---

## Configuration and customization

Edit these parameters in the notebook:

- Residents and hospitals
  - Residents: `residents = [f"{i:04d}" for i in range(1, 301)]`
  - Hospitals: `hospitals = [f"{i:04d}" for i in range(9001, 9331)]`

- Preference length per resident
  - In `generate_prefs()`, adjust `k = random.randint(10, 20)`

- Capacities
  - Global capacity: set `indvcapacity = 1` (or per‑hospital vector)

- Random seed
  - Reproducibility: `random.seed(42)`

- Integrality
  - Switch LP variables to binary: `cat="Binary"` in `LpVariable(...)` if desired

- Solver
  - PuLP uses CBC by default: `pulp.PULP_CBC_CMD(msg=False)`

---

## Outputs and interpretation

Files written during a run:
- `residents_prefs.xlsx` — synthetic residents and their preference lists
- `hospital_capacities.xlsx` — hospitals and capacities
- `preferences.csv` — dense preference matrix (rows= residents, cols= hospitals, values = rank; high value for unlisted)
- `assignments.csv` — assigned hospital indices for each resident (or `-1` if unmatched in other settings)

Console outputs:
- Problem status (“Optimal” when solved)
- Total matches locked
- Rank‑maximal signature: how many residents receive each rank \(r\)
- Sample of matched pairs: list of `(resident_id, hospital_id)`

Tip: If you include the `"None"` hospital, everyone will be matched to something; in that case “unmatched” is zero, and some assignments may go to `"None"` (interpreted as not placed).

---

## Evaluation metrics and plots

The notebook includes an evaluator that consumes `preferences.csv` and `assignments.csv`:

- First‑choice matches
- Unmatched count (when applicable)
- Weighted score \( \sum_i \frac{1}{\text{rank}_i} \)
- Average assigned rank
- Histogram of assignment outcomes (ranks + unmatched)

Sample results:
```python
{'first_choice_matches': 195,
 'unmatched_doctors': 0,
 'weighted_score': 234.6038059163059,
 'average_rank': 1.86}
```

A bar chart visualizes the distribution of assigned ranks.

---

## Troubleshooting

- Missing solver / CBC not found
  - PuLP bundles CBC on most platforms. If you see solver errors, reinstall PuLP or install CBC from your package manager (e.g., `conda install -c conda-forge coincbc`).

- Excel read/write errors
  - Install `openpyxl`. Ensure files aren’t open in Excel while writing.

- ID formatting
  - IDs are zero‑padded strings (e.g., `"0001"`, `"9001"`). If loading your own data, ensure IDs match the expected 4‑digit format or let the notebook normalize them.

- Preferences include unknown hospitals
  - The loader filters out hospitals not in `hospital_capacities.xlsx`.

- Ties in rankings
  - The demo assumes strict rankings per resident (order in the list). If you need ties, you’ll need to adapt the model.

---
