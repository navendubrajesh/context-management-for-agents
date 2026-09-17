package contextskills

test_allow_when_rbac_and_no_denials {
    allow with input as {
        "rbac_allowed": true,
        "skill": "evaluation",
        "model": "",
        "denied_skills": [],
        "denied_models": [],
    }
}

test_deny_when_skill_denied {
    not allow with input as {
        "rbac_allowed": true,
        "skill": "advanced-evaluation",
        "model": "",
        "denied_skills": ["advanced-evaluation"],
        "denied_models": [],
    }
}

test_require_approval_for_publish {
    require_approval with input as {"operation": "skills:publish"}
}
