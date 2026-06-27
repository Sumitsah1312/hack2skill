from rank_bm25 import BM25Okapi
import numpy as np

STOPWORDS = {
    "and","or","the","is","are",
    "with","for","of","to","a",
    "an","in","on","at","by"
}

def tokenize(text):

    text = text.lower()

    tokens = text.split()

    return [
        t.strip(".,()[]{}")
        for t in tokens
        if t not in STOPWORDS
        and len(t) > 2
    ]


def retrieve_candidates(
    jd_text,
    candidates,
    top_k=3000
):

    corpus = [
        tokenize(
            c["keyword_text"]
        )
        for c in candidates
    ]

    bm25 = BM25Okapi(corpus)

    query = tokenize(jd_text)

    scores = bm25.get_scores(query)

    top_idx = np.argsort(scores)[::-1][:top_k]

    shortlisted = []

    for idx in top_idx:

        c = candidates[idx]

        c["keyword_score"] = float(
            scores[idx]
        )

        shortlisted.append(c)

    return shortlisted