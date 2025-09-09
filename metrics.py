import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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


# ====== Example ======
if __name__ == "__main__":
    # 3 doctors, 3 hospitals
    prefs = np.array([
        [1, 2, 3, 5, 4],
        [3, 1, 2, 4, 5],
        [2, 3, 1, 5, 4],
        [3, 1, 2, 4, 5],
        [3, 2, 1, 4, 5],
    ])

    assignments = np.array([0, 1, -1, 1, 4])

    result = evaluate_matching(prefs, assignments)
    print(result)