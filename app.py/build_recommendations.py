import json
import os
import pickle
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    here = Path(__file__).resolve().parent

    movies_dict_path = here / "Movie_dict.pkl"
    similarity_path = here / "Similarity.pkl"
    out_path = here / "recommendations.json"

    if not movies_dict_path.exists():
        raise FileNotFoundError(f"Missing {movies_dict_path}")
    if not similarity_path.exists():
        raise FileNotFoundError(f"Missing {similarity_path}")

    movies_dict = pickle.load(open(movies_dict_path, "rb"))
    movies = pd.DataFrame(movies_dict)

    similarity = pickle.load(open(similarity_path, "rb"))
    similarity = np.asarray(similarity)

    if "title" not in movies.columns:
        raise KeyError("Movie_dict.pkl must contain a 'title' column")

    titles = movies["title"].astype(str).tolist()
    n = len(titles)

    # Build a lightweight lookup: { title: [recommended_title_1..5] }
    # Using argpartition keeps this fast for large matrices.
    recs: dict[str, list[str]] = {}
    for i in range(n):
        row = similarity[i]
        if row.shape[0] != n:
            raise ValueError("Similarity matrix size does not match movies list")

        # Get top 6 indices (includes itself), then sort by score desc.
        k = min(6, n)
        top_idx = np.argpartition(-row, range(k))[:k]
        top_idx = top_idx[np.argsort(-row[top_idx])]
        top_idx = [int(x) for x in top_idx if int(x) != i][:5]
        recs[titles[i]] = [titles[j] for j in top_idx]

    payload = {
        "generated_from": {
            "movies": os.fspath(movies_dict_path.name),
            "similarity": os.fspath(similarity_path.name),
        },
        "count": n,
        "recommendations": recs,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {out_path} with {n} movies")


if __name__ == "__main__":
    main()

