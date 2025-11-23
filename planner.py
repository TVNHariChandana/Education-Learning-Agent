def create_study_plan(hours, subject="General"):
    plan = []

    if hours <= 1:
        plan.append(f"• 30 min: Study your weakest topic in {subject}")
        plan.append(f"• 30 min: Quick revision in {subject}")
    
    elif hours == 2:
        plan.append(f"• 40 min: Practice {subject} exercises")
        plan.append(f"• 40 min: Revise concepts")
        plan.append(f"• 40 min: Notes review")
    
    elif hours >= 3:
        plan.append(f"• 1 hour: {subject} main topic")
        plan.append(f"• 1 hour: {subject} exercises")
        plan.append(f"• 1 hour: Revision")
        plan.append(f"• 30 min: Notes and review")
    
    return plan