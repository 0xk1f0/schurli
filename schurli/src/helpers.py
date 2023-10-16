def access_check(user_id, admin_list, privileged=False):
    if privileged:
        if not user_id in admin_list:
            return "You are not an admin!"
    return True
