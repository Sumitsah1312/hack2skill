import re
from collections import Counter
from docx import Document


# ==================================================
# LOAD JD
# ==================================================

def load_jd(path):

    doc = Document(path)

    text = "\n".join(
        para.text.strip()
        for para in doc.paragraphs
        if para.text.strip()
    )

    return text


# ==================================================
# GENERIC HELPERS
# ==================================================

def extract_section(text, start, end=None):

    start_idx = text.find(start)

    if start_idx == -1:
        return ""

    if end:

        end_idx = text.find(end)

        if end_idx == -1:
            return text[start_idx:]

        return text[start_idx:end_idx]

    return text[start_idx:]


def extract_bullets(section):

    bullets = []

    for line in section.split("\n"):

        line = line.strip()

        if not line:
            continue

        if (
            line.startswith("•")
            or line.startswith("-")
            or line.startswith("*")
        ):
            bullets.append(
                line[1:].strip()
            )

    return bullets


# ==================================================
# TITLE
# ==================================================

def extract_title(text):

    match = re.search(
        r"Job Description:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return lines[0] if lines else ""


# ==================================================
# EXPERIENCE
# ==================================================

def extract_experience(text):

    patterns = [

        r'Experience Required:\s*(\d+)\s*[–-]\s*(\d+)',

        r'(\d+)\s*[–-]\s*(\d+)\s*years',

        r'(\d+)\+\s*years'
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        nums = [
            int(x)
            for x in match.groups()
            if x
        ]

        if len(nums) == 2:

            return {
                "min": nums[0],
                "max": nums[1]
            }

        if len(nums) == 1:

            return {
                "min": nums[0],
                "max": nums[0] + 3
            }

    return {
        "min": 0,
        "max": 50
    }


# ==================================================
# SENTENCES
# ==================================================

def extract_sentences(text):

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    return [
        s.strip()
        for s in sentences
        if len(s.strip()) > 20
    ]


# ==================================================
# KEYWORDS
# ==================================================

STOPWORDS = {

    "the","a","an","and","or","of",
    "to","in","for","with","on",
    "at","by","from","that","this",
    "will","would","should","could",
    "have","has","had","is","are",
    "be","been","being","you","your",
    "our","we","they","their",
    "them","it's","its","than",
    "into","also","about"
}


def extract_keywords(text, top_k=150):

    tokens = re.findall(
        r"[A-Za-z][A-Za-z0-9+#.\-/]{2,}",
        text
    )

    tokens = [

        t.lower()
        for t in tokens
        if t.lower() not in STOPWORDS
    ]

    freq = Counter(tokens)

    return [
        word
        for word, _
        in freq.most_common(top_k)
    ]


# ==================================================
# DYNAMIC CLASSIFICATION
# ==================================================

NEGATIVE_PATTERNS = [

    "not want",
    "don't want",
    "do not want",
    "not a fit",
    "will not move forward",
    "disqualifier",
    "must not",
    "reject",
    "avoid"
]


POSITIVE_PATTERNS = [

    "must have",
    "required",
    "experience with",
    "hands-on",
    "strong",
    "need",
    "looking for",
    "production experience"
]


def classify_sentences(sentences):

    positive = []
    negative = []
    neutral = []

    for sentence in sentences:

        s = sentence.lower()

        if any(
            pattern in s
            for pattern in NEGATIVE_PATTERNS
        ):
            negative.append(sentence)

        elif any(
            pattern in s
            for pattern in POSITIVE_PATTERNS
        ):
            positive.append(sentence)

        else:
            neutral.append(sentence)

    return positive, negative, neutral


# ==================================================
# REDROB SECTION PARSING
# ==================================================

def parse_redrob_sections(text):

    required_section = extract_section(
        text,
        "Things you absolutely need",
        "Things we'd like you to have"
    )

    preferred_section = extract_section(
        text,
        "Things we'd like you to have",
        "Things we explicitly do NOT want"
    )

    negative_section = extract_section(
        text,
        "Things we explicitly do NOT want"
    )

    required = [
        line.strip()
        for line in required_section.split("\n")
        if line.strip()
        and "Things you absolutely need" not in line
    ]

    preferred = [
        line.strip()
        for line in preferred_section.split("\n")
        if line.strip()
        and "Things we'd like you to have" not in line
    ]

    negative = [
        line.strip()
        for line in negative_section.split("\n")
        if line.strip()
        and "Things we explicitly do NOT want" not in line
    ]

    return required, preferred, negative


# ==================================================
# BUILD BM25 TEXT
# ==================================================

def build_jd_keyword_text(jd_profile):

    return " ".join([

        jd_profile["title"],

        jd_profile["required_text"],

        jd_profile["preferred_text"],

        jd_profile["responsibility_text"],

        jd_profile["keyword_text"]
    ])


# ==================================================
# MAIN ANALYZER
# ==================================================

def analyze_jd(text):

    title = extract_title(text)

    experience = extract_experience(text)

    required, preferred, negative = (
        parse_redrob_sections(text)
    )

    sentences = extract_sentences(text)

    dyn_positive, dyn_negative, neutral = (
        classify_sentences(sentences)
    )

    # fallback if section parsing weak

    if len(required) < 3:
        required.extend(dyn_positive)

    if len(negative) < 2:
        negative.extend(dyn_negative)

    responsibilities = [

        s
        for s in neutral
        if len(s) > 40
    ][:40]

    keywords = extract_keywords(text)

    return {

        "title": title,

        "min_exp":
            experience["min"],

        "max_exp":
            experience["max"],

        "required":
            required,

        "preferred":
            preferred,

        "negative":
            negative,

        "responsibilities":
            responsibilities,

        "keywords":
            keywords,

        "required_text":
            " ".join(required),

        "preferred_text":
            " ".join(preferred),

        "negative_text":
            " ".join(negative),

        "responsibility_text":
            " ".join(responsibilities),

        "keyword_text":
            " ".join(keywords),

        "all_text":
            text
    }