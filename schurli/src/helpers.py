def access_check(user_id, admin_list, block_list, privileged=False):
    if privileged:
        if not user_id in admin_list:
            return "You are not an admin!"
        else:
            return True
    if user_id in block_list:
        return "You are currently on the blocklist!"
    return True
