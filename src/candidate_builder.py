
def build_candidate_text(candidate):

    parts = []

    profile = candidate["profile"]

    parts.append(
        f"TITLE: {profile.get('current_title','')}"
    )

    parts.append(
        f"HEADLINE: {profile.get('headline','')}"
    )

    parts.append(
        f"SUMMARY: {profile.get('summary','')}"
    )

    for job in candidate["career_history"]:

        parts.append(
            f"EXPERIENCE_TITLE: {job.get('title','')}"
        )

        parts.append(
            f"EXPERIENCE_DESC: {job.get('description','')}"
        )

    for skill in candidate["skills"]:

        parts.append(
            f"SKILL: {skill.get('name','')}"
        )

    return "\n".join(parts)

def build_skills_text(candidate):

    return " ".join(
        skill.get("name", "")
        for skill in candidate.get("skills", [])
    )


def build_industry_text(candidate):

    industries = []

    for job in candidate.get("career_history", []):

        industry = job.get("industry", "")

        if industry:
            industries.append(industry)

    return " ".join(industries)


def calculate_leadership_score(candidate):

    leadership_keywords = {
        "lead",
        "manager",
        "head",
        "director",
        "principal",
        "staff",
        "architect",
        "vp",
        "chief"
    }

    score = 0

    for job in candidate.get("career_history", []):

        title = job.get("title", "").lower()

        if any(
            keyword in title
            for keyword in leadership_keywords
        ):
            score += 1

    return score

def build_candidate_profile(candidate):

    profile = candidate["profile"]
    signals = candidate["redrob_signals"]

    # Career Text
    career_parts = []

    career_parts.append(
        f"CURRENT_TITLE: {profile.get('current_title', '')}"
    )

    for job in candidate.get("career_history", [])[:5]:

        career_parts.append(
            f"ROLE: {job.get('title', '')}"
        )

        career_parts.append(
            f"INDUSTRY: {job.get('industry', '')}"
        )

        career_parts.append(
            f"DESCRIPTION: {job.get('description', '')[:500]}"
        )

    career_text = "\n".join(career_parts)
    

    # Skills Text
    skills_text = " ".join(
        skill.get("name", "")
        for skill in candidate["skills"]
    )

    industry_text = build_industry_text(candidate)

    leadership_score = calculate_leadership_score(
        candidate
    )

    # Full Text
    full_text = build_candidate_text(candidate)
    rank_text = f"""
                CURRENT_TITLE:
                {profile.get('current_title', '')}

                HEADLINE:
                {profile.get('headline', '')}

                SUMMARY:
                {profile.get('summary', '')}

                SKILLS:
                {skills_text}

                CAREER:
                {career_text}
                """
    keyword_text = " ".join([
                profile.get("current_title", ""),
                profile.get("headline", ""),
                skills_text,
                industry_text,
                career_text
            ])
    
    # Behavior Signals
    behavior = {

        "open_to_work":
            signals["open_to_work_flag"],

        "response_rate":
            signals["recruiter_response_rate"],

        "last_active":
            signals["last_active_date"],

        "notice_period":
            signals["notice_period_days"],

        "github_score":
            signals["github_activity_score"],

        "saved_by_recruiters":
            signals["saved_by_recruiters_30d"],

        "interview_completion":
            signals["interview_completion_rate"],

        "profile_completeness":
            signals["profile_completeness_score"]
    }

    return {

        "candidate_id":
            candidate["candidate_id"],

        "current_title":
            profile["current_title"],

        "experience":
            profile["years_of_experience"],

        "career_text":
            career_text,

        "skills_text":
            skills_text,

        "full_text":
            full_text,
        
        "rank_text":
            rank_text,
            
        "keyword_text": keyword_text,

        "behavior":
            behavior,
        
        "industry_text":
            industry_text,

        "leadership_score":
            leadership_score,
        
        "career_embedding": None,
        "skill_embedding": None
        # "title_embedding": None,
    }