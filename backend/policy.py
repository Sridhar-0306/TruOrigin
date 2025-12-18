# ==============================
# POLICY ENGINE – AI_auth_MVP
# ==============================

# Possible detection statuses
AI_AUTHENTIC = "AI_GENERATED_AUTHENTIC"
TAMPERED = "TAMPERED"
UNVERIFIED = "NO_VERIFIABLE_SIGNATURE"

# Possible enforcement decisions
ALLOW = "ALLOW"
WARN = "WARN"
BLOCK = "BLOCK"


# ==============================
# POLICY TABLE
# ==============================

POLICY_RULES = {
    "legal_government": {
        AI_AUTHENTIC: BLOCK,
        TAMPERED: BLOCK,
        UNVERIFIED: BLOCK
    },
    "education_exam": {
        AI_AUTHENTIC: BLOCK,
        TAMPERED: BLOCK,
        UNVERIFIED: BLOCK
    },
    "healthcare_medical": {
        AI_AUTHENTIC: BLOCK,
        TAMPERED: BLOCK,
        UNVERIFIED: BLOCK
    },
    "media_marketing": {
        AI_AUTHENTIC: WARN,
        TAMPERED: BLOCK,
        UNVERIFIED: WARN
    },
    "creative_entertainment": {
        AI_AUTHENTIC: ALLOW,
        TAMPERED: BLOCK,
        UNVERIFIED: ALLOW
    }
}


# ==============================
# POLICY ENFORCEMENT FUNCTION
# ==============================

def enforce_policy(detection_status, context):
    """
    Enforces policy based on detection status and usage context
    """

    context = context.lower()

    if context not in POLICY_RULES:
        return {
            "decision": BLOCK,
            "reason": "Unknown usage context"
        }

    decision = POLICY_RULES[context].get(detection_status, BLOCK)

    reason_map = {
        BLOCK: "Content not permitted in this context",
        WARN: "AI-generated or unverified content – disclosure required",
        ALLOW: "Content permitted"
    }

    return {
        "decision": decision,
        "reason": reason_map[decision]
    }


# ==============================
# CLI TEST
# ==============================

if __name__ == "__main__":

    test_cases = [
        ("AI_GENERATED_AUTHENTIC", "legal_government"),
        ("NO_VERIFIABLE_SIGNATURE", "education_exam"),
        ("AI_GENERATED_AUTHENTIC", "media_marketing"),
        ("TAMPERED", "creative_entertainment"),
        ("NO_VERIFIABLE_SIGNATURE", "creative_entertainment"),
    ]

    for status, context in test_cases:
        print(f"\nStatus: {status}, Context: {context}")
        print(enforce_policy(status, context))
