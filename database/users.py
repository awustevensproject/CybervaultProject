"""
Simulated in-memory database
DO NOT use real database yet (Day 2 topic)
"""

def get_user(username):
    fake_users = {
        "admin": {
            "username": "admin",
            "password": "hashed_admin123"
        },
        "student": {
            "username": "student",
            "password": "hashed_pass"
        }
    }

    return fake_users.get(username)