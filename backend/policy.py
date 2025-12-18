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

def enforce_policy(status, context):
    """
    Enforces context-aware rules WITHOUT blocking unsigned content.
    """

    context = context.lower()

    # 🚫 Always block tampered content
    if status == "TAMPERED":
        return {
            "decision": "BLOCK",
            "reason": "Content integrity compromised (tampered)"
        }

    # ⚠️ AI-generated content rules
    if status == "AI_GENERATED_AUTHENTIC":
        if context in ["legal_government", "government"]:
            return {
                "decision": "WARN",
                "reason": "AI-generated content requires disclosure and approval in government context"
            }

        if context in ["education_exam", "education"]:
            return {
                "decision": "WARN",
                "reason": "AI-generated content flagged for academic integrity review"
            }

        if context in ["media_marketing", "media"]:
            return {
                "decision": "WARN",
                "reason": "AI-generated content must be disclosed"
            }

        # Creative, general use
        return {
            "decision": "ALLOW",
            "reason": "AI-generated content allowed"
        }

    # ✅ Unsigned / unknown content (IMPORTANT CHANGE)
    if status == "NO_VERIFIABLE_SIGNATURE":
        return {
            "decision": "ALLOW",
            "reason": "Content origin unknown; allowed under standard rules"
        }

    # Fallback (should not hit)
    return {
        "decision": "ALLOW",
        "reason": "No restrictions applied"
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
