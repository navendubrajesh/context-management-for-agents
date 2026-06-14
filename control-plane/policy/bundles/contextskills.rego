package contextskills

default allow = false

allow {
  input.rbac_allowed == true
  not skill_denied
  not model_denied
}

skill_denied {
  input.skill != ""
  input.skill == input.denied_skills[_]
}

model_denied {
  input.model != ""
  input.model == input.denied_models[_]
}

require_approval {
  input.operation == "skills:publish"
}

require_approval {
  input.operation == "tenants:manage"
}
