TASK_TEMPLATES = {
    "reset_password": "Reset the password for {email} and report the new temporary password.",

    "create_user": (
        "Create a new user with email {email}, full name '{full_name}', "
        "department '{department}'. Set status to active."
    ),

    "suspend_user": "Suspend the user account for {email}. Confirm the suspension was successful.",

    "activate_user": "Activate the suspended user account for {email}.",

    "assign_license": "Assign the '{license}' license to {email}.",

    "check_and_create": (
        "Check if a user with email {email} exists. "
        "If they do not exist, create them with full name '{full_name}' and department '{department}'. "
        "Then assign them the '{license}' license. "
        "Report each step and the final state."
    ),

    "full_onboard": (
        "Onboard a new employee: email={email}, name='{full_name}', department='{department}'. "
        "Steps: 1) Check if user already exists. 2) If not, create the user. "
        "3) Reset their password to get a temporary password. "
        "4) Assign them 'Microsoft 365' and 'Slack Pro' licenses. "
        "Report the temp password and confirm all licenses are assigned."
    ),
}

def build_task(template_key: str, **kwargs) -> str:
    return TASK_TEMPLATES[template_key].format(**kwargs)