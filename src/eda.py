import time
import json
import numpy as np
import pandas as pd
import zipfile

from datetime import datetime

from candidate_builder import build_candidate_profile
from sentence_transformer_model import model

from retriever import retrieve_candidates

from jd_parser import (
    load_jd,
    analyze_jd,
    build_jd_keyword_text
)

from ranker import rank_all_candidates


# ==================================================
# START
# ==================================================

start_time = time.time()

print(
    "Started:",
    datetime.now().strftime("%H:%M:%S")
)


# ==================================================
# LOAD JD
# ==================================================

print("Loading JD...")

jd_text = load_jd(
    "../data/job_description.docx"
)

jd_profile = analyze_jd(
    jd_text
)

jd_keyword_text = build_jd_keyword_text(
    jd_profile
)

print("JD Loaded")


# ==================================================
# Generate Reasoning
# ==================================================
def generate_reasoning(candidate):

    parts = []

    if candidate.get("current_title"):
        parts.append(
            candidate["current_title"]
        )

    if candidate.get("experience_score", 0) > 0.8:
        parts.append(
            "strong experience alignment"
        )

    if candidate.get("semantic_score", 0) > 0.75:
        parts.append(
            "high semantic JD match"
        )

    if candidate.get("behavior_score", 0) > 0.70:
        parts.append(
            "strong recruiter engagement"
        )

    if candidate.get("recruitability_score", 0) > 0.70:
        parts.append(
            "good hiring likelihood"
        )

    return "; ".join(parts)

# ==================================================
# LOAD CANDIDATES
# ==================================================

candidate_list = []

print("Loading Candidates...")


with zipfile.ZipFile("../data/candidates.zip", "r") as z:
    with z.open("candidates.jsonl") as f:
        for line in f:

            candidate = json.loads(line)

            candidate_profile = (
                build_candidate_profile(
                    candidate
                )
            )

            candidate_list.append(
                candidate_profile
            )

print(
    f"Loaded {len(candidate_list)} candidates"
)


# ==================================================
# STAGE 1
# BM25 RETRIEVAL
# ==================================================

print(
    "\nStage 1 : BM25 Retrieval..."
)

shortlisted = retrieve_candidates(
    jd_keyword_text,
    candidate_list,
    top_k=2000
)

print(
    f"Retrieved {len(shortlisted)} candidates"
)


# ==================================================
# STAGE 2
# SEMANTIC RETRIEVAL
# ==================================================

print(
    "\nStage 2 : Semantic Ranking..."
)

texts = [
    c["rank_text"]
    for c in shortlisted
]

candidate_embeddings = model.encode(
    texts,
    batch_size=512,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True
)
jd_rank_text = " ".join([

    jd_profile["title"],

    jd_profile["required_text"],

    jd_profile["preferred_text"],

    jd_profile["responsibility_text"]
])


jd_embedding = model.encode(
    jd_rank_text,
    convert_to_numpy=True,
    normalize_embeddings=True
)

semantic_scores = (
    candidate_embeddings
    @ jd_embedding
)

for candidate, score in zip(
    shortlisted,
    semantic_scores
):

    candidate["semantic_score"] = (
        float(score)
    )


# ==================================================
# NORMALIZE BM25
# ==================================================

bm25_scores = np.array([
    c["keyword_score"]
    for c in shortlisted
])

mn = bm25_scores.min()
mx = bm25_scores.max()

for candidate in shortlisted:

    candidate["keyword_score_norm"] = (
        (
            candidate["keyword_score"]
            - mn
        )
        /
        (
            mx - mn + 1e-8
        )
    )

    candidate["retrieval_score"] = (
    0.35 * candidate["keyword_score_norm"]
    +
    0.65 * candidate["semantic_score"]
    )


# ==================================================
# TOP 300
# ==================================================

shortlisted.sort(
    key=lambda x:
    x["retrieval_score"],
    reverse=True
)

top300 = shortlisted[:300]

print(
    f"Top 300 selected"
) 


# ==================================================
# STAGE 3
# FINAL RANKING
# ==================================================

print(
    "\nStage 3 : Final Ranking..."
)

result = rank_all_candidates(
    top300
)

top100 = result[:100]


# ==================================================
# CSV EXPORT
# ==================================================

rows = []

for rank, candidate in enumerate(
    top100,
    start=1
):

    rows.append({
        "candidate_id": candidate["candidate_id"],
        "rank": rank,
        "score": candidate["final_score"],
        "reasoning": generate_reasoning(candidate)
    })

submission_df = pd.DataFrame(
    rows
)

submission_df.to_csv(
    "../submission.csv",
    index=False
)

print(
    "\nsubmission.csv generated"
)

print(
    f"Top 100 exported"
)


# ==================================================
# DISPLAY TOP 10
# ==================================================

print("\nTOP 10\n")

for r in top100[:10]:

    print(
        f"{r['candidate_id']} | "
        f"{r['current_title']} | "
        f"{round(r['final_score'],4)}"
    )


# ==================================================
# END
# ==================================================

end_time = time.time()

print(
    f"\nTime Taken: "
    f"{round(end_time-start_time,2)} seconds"
)