import pulp
import pandas as pd
import random
import matplotlib.pyplot as plt
import argparse


def load_inputs(pref_path, cap_path):
    import pandas as pd

    # Load Excel files and read the Excel files into dataframes. 
    # We assume the Excel file "residents_prefs.xlsx" has two columns, one with the resident's name labeled "Names",  
    # one with list of preferences separated by commas, in order of rank.
    # For example:
    #    Names     Preferences
    # 0   r1        A,B,C,D
    # 1   r2        B,D
    # 2   r3        A,B,F,G,H
    #
    # This signifies that Dr. r1's rankings are 1. A, 2. B, 3. C, 4. D. And so on.
    # For "hospital_capacities.xlsx", we assume that the first column is labeled "Hospital", and the second one is labeled "Capacity".
    # The columns for hospital_capacities.xlsx should be strings for Hospital, int for Capacity.

    df = pd.read_excel(pref_path)
    cap_df = pd.read_excel(cap_path)    # columns: Hospital, Capacity



    # Proceed to read the residents Excel file into a dict(string,list). The list will also be ordered by rank. 
    residents = df["Names"].astype(str).tolist()

    # Append "None" to list of hospitals, with excess capacity. 
    cap_df.loc[len(cap_df)] = ["None", len(residents)+1]

    # Normalize formatting
    cap_df = cap_df.copy()
    cap_df["Hospital"] = cap_df["Hospital"].astype(str).str.strip().str.zfill(4)
    cap_df["Capacity"] = cap_df["Capacity"].astype(int).clip(lower=0)

    hospitals = dict(zip(cap_df["Hospital"], cap_df["Capacity"]))

    preferences = {}
    for _, row in df.iterrows():
        name = str(row["Names"]).strip()
        pref_str = str(row["Preferences"]) if pd.notna(row["Preferences"]) else ""
        raw_list = [p.strip() for p in pref_str.split(",") if p.strip()]

        # normalize & filter
        hospital_list = []
        for h in raw_list:
            h_norm = str(h).strip().zfill(4)  
            if h_norm in hospitals:
                hospital_list.append(h_norm)
    
        # Append the created hospital "None" at the end of each resident's preference list
        hospital_list.append("None")

        # to (hospital, rank) tuples: 1,2,3,...
        preferences[name] = [(h, r+1) for r, h in enumerate(hospital_list)]
    
    
    



    return residents, hospitals, preferences, hospital_list, indvcapacity


def build_model(residents, hospitals, preferences, hospital_capacities, indvcapacity):
    # edges is a list of all possible triplets (i,j,r) for which i and j are "successful" rank-r pairings. 
    # For example, (0001, 9058, 1) would be an element of edges if and only if doctor 0001 selected hospital 9058 as their #1 choice
    # These pairs will later be used to determine maximum rank pairs.

    edges = []  # list of (resident, hospital, rank)
    for i in residents:
        for (j, r) in preferences.get(i, []):
            edges.append((i, j, r))

    if not edges:
        raise ValueError("No edges found from preferences after normalization.")

    max_rank = max(r for (_, _, r) in edges)



    # Create Linear Programming problem in PuLP, Rank_Maximal_AllRanks, and sets the problem to maximize.
    prob = pulp.LpProblem("RankMaximal_AllRanks", pulp.LpMaximize)


    # Create decision variable x. Xij = 1 if we assign resident i to hospital j, and 0 otherwise.
    x = {(i, j): pulp.LpVariable(f"x_{i}_{j}", lowBound=0, upBound=1, cat="Continuous")
         for (i, j, _) in edges}


    # Adds constraint that any resident i can only be assigned to maximum of one hospital. I.e. sum of xi over j is 1.
    for i in residents:
        prob += (
            pulp.lpSum(x[(ii, j)] for (ii, j) in x.keys() if ii == i) <= 1,
            f"Resident_{i}_at_most_one"
        )


    # Adds constraint that any hospital j must have less residents than its capacity.
    for j, cap in hospitals.items():
        prob += (
            pulp.lpSum(x[(i, jj)] for (i, jj) in x.keys() if jj == j) <= int(cap),
            f"Hospital_{j}_capacity"
        )


    # Helpful variables to assist with maximizing
    # all_match_expr is the sum of all decision variables across all hospitals and all residents. It represents the # of assignments that have been made
    all_match_expr = pulp.lpSum(x.values())

    # Building rank_expr as the vector {r1,r2,r3...} that represents how many assignments are made at each rank. I.e {103, 4, 3,...} would represent 
    # 103 first rank matches, 4 second rank matches, 3 third rank matches, etc. 
    rank_expr = {}

    for r in range(1, max_rank + 1):
        rank_expr[r] = pulp.lpSum(x[(i, j)] for (i, j, rr) in edges if rr == r)
        
    return prob, x, z, edges, max_rank, signature, K_total


def solve_model(prob, x, z, edges, max_rank, signature, K_total):
    # First we set objective to our previously defined variable all_match_expr to maximize TOTAL assignments
    prob.setObjective(all_match_expr)

    # Solve the linear program and check that an optimal solution was found.
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[prob.status] != "Optimal":
        raise RuntimeError("All matching not Optimal.")

    # Extract the maximum number of total assignments as K_Total.
    K_total = int(round(pulp.value(all_match_expr)))

    locks = []
    signature = {}
    
    # "Lock" all_match_expr to K_Total, i.e. there cannot be less assignments than the maximum number of assignments.
    prob += (all_match_expr == K_total), "LOCK_total_matches"
    locks.append(("total", K_total))

    # Set up for loop for all ranks
    for r in range(1, max_rank + 1):
    
        # Set the objective as maximizing assignments for the current rank.
        prob.setObjective(rank_expr[r])
    
        # Solve and check for optimal solution.
        prob.solve(pulp.PULP_CBC_CMD(msg=False))
        if pulp.LpStatus[prob.status] != "Optimal":
            raise RuntimeError(f"{r} assignments not Optimal.")
        
        # Extract the maximum number of assignments for current rank w/ given constraints.
        Kr = int(round(pulp.value(rank_expr[r])))

        # Stores number of residents matched at that rank as signature[r]
        signature[r] = Kr

        # "Lock" rank_expr[r] == Kr by adding this as a constraint. 
        prob += (rank_expr[r] == Kr), f"LOCK_rank_{r}"
        locks.append((r, Kr))


    # Once exact maximum numbers for each rank are found, extract one feasible solution.
    prob.setObjective(pulp.lpSum(0 * v for v in x.values()))
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    print("Final Status:", pulp.LpStatus[prob.status])



    return prob, x, signature, K_total, max_rank


def extract_results(residents, hospitals, x, max_rank, signature, K_total):
    
    # Build the matching list from the optimal solution
    matching = []
    for (i, j), var in x.items():
        val = var.value()
        if val is not None and val >= 1 - 1e-6:
            matching.append((i, j))

    # Print Results 
    print(f"# residents: {len(residents)}")
    print(f"# hospitals: {len(hospitals)}")
    print(f"Locked total matches: {K_total}")
    print("Rank-maximal signature (count per rank):")
    for r in range(1, max_rank + 1):
        print(f"  rank {r}: {signature.get(r, 0)}")
    print(f"# matched pairs in solution: {len(matching)}")

    return matching, signature


def _attach_eval_utils():
    
    def load_data(pref_file, assign_file):
        preferences = pd.read_csv(pref_file, header=None).to_numpy()
        assignments = pd.read_csv(assign_file, header=None).to_numpy().flatten()
        return preferences, assignments

    def evaluate_matching(preferences, assignments, plot_histogram=True):

        num_doctors, num_hospitals = preferences.shape

        # The first-choice hospital for each doctor (hospital ID with the smallest preference value)
        first_choices = np.argmin(preferences, axis=1)

        # Number of doctors matched to their first-choice hospital
        matched_first_choice = np.sum(assignments == first_choices)

        # Number of doctors who were not matched
        unmatched_count = np.sum(assignments == -1)

        # Weighted score: 1 for first choice, 1/2 for second choice, 1/3 for third, etc.
        weighted_score = 0
        ranks = []  # store each doctor's assigned rank
        for i, hospital in enumerate(assignments):
            if hospital == -1:
                continue
            # Find the rank of the assigned hospital for this doctor
            rank = np.argsort(preferences[i]).tolist().index(hospital) + 1
            ranks.append(rank)
            weighted_score += 1 / rank

        # Average rank
        avg_rank = float(np.mean(ranks)) if ranks else None

        # Plot histogram of ranks if requested
        if plot_histogram and ranks:
            values = ranks + [0] * unmatched_count  # 0 unmatched
            labels = [f"Rank {i}" for i in range(1, max(ranks) + 1)] + ["Unmatched"] if ranks else ["Unmatched"]

            counts = [values.count(0)] + [values.count(i) for i in range(1, max(ranks) + 1)] if ranks else [unmatched_count]

            plt.bar(range(len(counts)), counts, tick_label=labels, width=0.6)
            plt.xlabel("Assignment outcome")
            plt.ylabel("Number of doctors")
            plt.title("Distribution of assigned preferences")
            plt.show()


        return {
            "first_choice_matches": int(matched_first_choice),
            "unmatched_doctors": int(unmatched_count),
            "weighted_score": float(weighted_score),
            "average_rank": avg_rank
        }

    import numpy as np  

    # Map hospitals and residents to indices for matrix form 
    resident_to_idx = {res: idx for idx, res in enumerate(residents)}   
    hospital_list = sorted(hospitals.keys())                           
    hospital_to_idx = {h: idx for idx, h in enumerate(hospital_list)}   

    # Build preference matrix: rows=residents, cols=hospitals, values=ranks 
    pref_matrix = np.full((len(residents), len(hospital_list)), fill_value=9999)  
    for i, prefs in preferences.items():                                         
        for h, r in prefs:                                                        
            pref_matrix[resident_to_idx[i], hospital_to_idx[h]] = r               

    # Build assignment vector: hospital index or -1 if unmatched 
    assign_vector = np.full(len(residents), -1)                                   
    for i, j in matching:                                                         
        ri = resident_to_idx[i]                                                  
        hj = hospital_to_idx[j]                                                   
        assign_vector[ri] = hj                                                    

    # Save to CSV for evaluation function 
    np.savetxt("preferences.csv", pref_matrix, delimiter=",", fmt="%d")           
    np.savetxt("assignments.csv", assign_vector, delimiter=",", fmt="%d")         


    from matplotlib import pyplot as plt   

    # Use the evaluation code
    preferences_arr, assignments_arr = load_data("preferences.csv", "assignments.csv")   
    results = evaluate_matching(preferences_arr, assignments_arr, plot_histogram=True)   
    print(results)                                                                       

def export_matching_to_csv(matching, output_file="matching_results.csv"):
    # Exports list of pairs as a CSV
    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Resident", "Hospital"])
        for resident, hospital in matching:
            writer.writerow([resident, hospital])
    print(f"Matching results exported to {output_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefs", type=str, default=None)
    parser.add_argument("--caps", type=str, default=None)
    args = parser.parse_args()

    pref_path = args.prefs or input("Path to residents preferences Excel file: ").strip()
    cap_path = args.caps or input("Path to hospital capacities Excel file: ").strip()

    residents, hospitals, preferences, hospital_capacities, indvcapacity = load_inputs(pref_path, cap_path)
    prob, x, z, edges, max_rank, signature, K_total = build_model(residents, hospitals, preferences, hospital_capacities, indvcapacity)
    prob, x, signature, K_total, max_rank = solve_model(prob, x, z, edges, max_rank, signature, K_total)
    matching, signature = extract_results(residents, hospitals, x, max_rank, signature, K_total)
    export_matching_to_csv(matching, "results.csv")

if __name__ == "__main__":
    main()
