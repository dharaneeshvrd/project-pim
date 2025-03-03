import auth.auth as auth

def cleanup_and_exit(config, cookies, status):
    print("deleting user session")
    auth.delete_session(config, cookies)
    exit(status)
