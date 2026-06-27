def extract_features(candidate):
    features={}
    features["experience"]=candidate["profile"]["years_of_experience"]
    features["title"]=candidate["profile"]["current_title"]
    features["open_to_work"]=int(candidate["redrob_signals"]["open_to_work_flag"])
    features["github_score"] = candidate["redrob_signals"]["github_activity_score"]
    features["notice_period"] = (
        candidate["redrob_signals"]["notice_period_days"]
    )
    
    features["response_rate"] = (
        candidate["redrob_signals"]["recruiter_response_rate"]
    )
    
    features["profile_completeness"] = (
        candidate["redrob_signals"]["profile_completeness_score"]
    )
    
    features["saved_by_recruiters"] = (
        candidate["redrob_signals"]["saved_by_recruiters_30d"]
    )
    
    features["interview_completion_rate"] = (
        candidate["redrob_signals"]["interview_completion_rate"]
    )
    return features