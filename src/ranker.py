from datetime import datetime

from jd_parser import (
    load_jd,
    analyze_jd
)


# ---------------------------------
# Load JD Once
# ---------------------------------

print("Loading JD...")

jd_text = load_jd(
    "../data/job_description.docx"
)

jd_profile = analyze_jd(
    jd_text
)


# ---------------------------------
# Experience Score
# ---------------------------------
def experience_score(
    candidate_exp,
    min_exp,
    max_exp
):

    if candidate_exp is None:
        return 0

    if min_exp <= candidate_exp <= max_exp:
        return 100

    if candidate_exp < min_exp:

        gap = min_exp - candidate_exp

        return max(
            0,
            100 - gap * 15
        )

    gap = candidate_exp - max_exp

    return max(
        60,
        100 - gap * 3
    )

# ---------------------------------
# Recruitability Score
# ---------------------------------

def recruitability_score(behavior):

    score = 0

    if behavior["open_to_work"]:
        score += 30

    score += (
        behavior["response_rate"] * 30
    )

    score += min(
        behavior["saved_by_recruiters"] / 3,
        20
    )

    notice = behavior["notice_period"]

    if notice <= 30:
        score += 20

    elif notice <= 60:
        score += 10

    return min(score, 100)


# ---------------------------------
# Behavior Score
# ---------------------------------

def behavior_score(behavior):

    score = 0

    if behavior["open_to_work"]:
        score += 20

    score += (
        behavior["response_rate"] * 20
    )

    score += (
        behavior["interview_completion"] * 20
    )

    score += min(
        behavior["profile_completeness"] / 5,
        20
    )

    github = max(
        behavior["github_score"],
        0
    )

    score += min(
        github / 5,
        20
    )

    notice = behavior["notice_period"]

    if notice <= 30:
        score += 20

    elif notice <= 60:
        score += 10

    return min(
        score,
        100
    )


# ---------------------------------
# Activity Score
# ---------------------------------

def activity_score(behavior):

    try:

        last_active = datetime.strptime(
            behavior["last_active"],
            "%Y-%m-%d"
        )

        days = (
            datetime.now()
            - last_active
        ).days

        if days <= 7:
            return 100

        if days <= 30:
            return 80

        if days <= 90:
            return 60

        if days <= 180:
            return 40

        return 10

    except:
        return 0


# ---------------------------------
# Rank Single Candidate
# ---------------------------------
def rank_candidate(
    candidate_profile
):

    semantic_score = (
        candidate_profile[
            "semantic_score"
        ]
    )

    keyword_score = (
        candidate_profile[
            "keyword_score_norm"
        ]
    )

    exp_score = (
        experience_score(
            candidate_profile[
                "experience"
            ],
            jd_profile["min_exp"],
            jd_profile["max_exp"]
        )
        / 100
    )

    beh_score = (
        behavior_score(
            candidate_profile[
                "behavior"
            ]
        )
        / 100
    )

    act_score = (
        activity_score(
            candidate_profile[
                "behavior"
            ]
        )
        / 100
    )

    recruit_score = (
        recruitability_score(
            candidate_profile[
                "behavior"
            ]
        )
        / 100
    )

    leadership_score = min(
        candidate_profile.get(
            "leadership_score",
            0
        ) / 5,
        1
    )

    feature_score = (

        0.30 * exp_score

        + 0.25 * beh_score

        + 0.15 * act_score

        + 0.20 * recruit_score

        + 0.10 * leadership_score
    )

    final_score = (

        0.20 * keyword_score

        + 0.45 * semantic_score

        + 0.35 * feature_score
    )

    return {

        "candidate_id":
            candidate_profile[
                "candidate_id"
            ],

        "current_title":
            candidate_profile[
                "current_title"
            ],

        "keyword_score":
            round(
                keyword_score,
                4
            ),

        "semantic_score":
            round(
                semantic_score,
                4
            ),

        "experience_score":
            round(
                exp_score,
                4
            ),

        "behavior_score":
            round(
                beh_score,
                4
            ),

        "activity_score":
            round(
                act_score,
                4
            ),

        "recruitability_score":
            round(
                recruit_score,
                4
            ),

        "leadership_score":
            round(
                leadership_score,
                4
            ),

        "feature_score":
            round(
                feature_score,
                4
            ),

        "final_score":
            round(
                final_score,
                4
            )
    }
# ---------------------------------
# Rank Multiple Candidates
# ---------------------------------

def rank_all_candidates(
    candidate_profiles
):

    results = []

    for candidate in candidate_profiles:

        result = rank_candidate(
            candidate
        )

        results.append(
            result
        )

    results.sort(
        key=lambda x: (
            -x["final_score"],
            x["candidate_id"]
        )
    )

    return results