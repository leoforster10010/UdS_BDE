from django.contrib.auth import get_user
from termcolor import colored

user_mapping = {
    "P": "a@b.de",
    "N": "unauthenticated",
}


def login_and_check_whether_user_logged_in_and_log_out(self, email, password="test"):
    """
    checks if a user can be logged in and out with the given password
    """
    # login
    login = self.client.login(email=email, password=password)

    # check that we are logged in:
    auth_user = get_user(self.client)
    self.assertTrue(auth_user.is_authenticated)
    self.assertEqual(email, auth_user.email)

    # logout:
    logout = self.client.logout()
    # check that we are logged out:
    auth_user = get_user(self.client)
    self.assertFalse(auth_user.is_authenticated)


def test_paths_for_allowed_and_forbidden_users(
    self, paths, users_allowed, users_forbidden
):
    """
    tests the list of paths against allowed and forbidden users
    users_allowed: string with one capital character per test_*-user
    users_forbidden: string with one capital character per test_*-user
    """

    # cases list to easily loop over allowed and forbidden users
    cases = [
        {"users": users_allowed, "status_code": [200]},
        {"users": users_forbidden, "status_code": [302, 403, 404, 500]},
    ]

    if "N" not in users_allowed and "N" not in users_forbidden:
        print("WARNING: no unauthenticated user in users_allowed or users_forbidden")
    for case in cases:
        users = case["users"]
        if users == "":
            continue
        status_code = case["status_code"]
        for u in users:
            user = user_mapping[u]
            no_login = False
            if user == "unauthenticated":
                no_login = True
            if not no_login:
                # login
                login = self.client.login(email=user, password="test")

                # check that we are logged in:
                auth_user = get_user(self.client)
                self.assertTrue(auth_user.is_authenticated)
                self.assertEqual(user, auth_user.email)

            # try all paths provided:
            for path in paths:
                response = self.client.get(path)
                try:
                    # self.assertEqual(response.status_code, status_code)
                    self.assertIn(response.status_code, status_code)
                except AssertionError:
                    print()
                    print(colored("AssertionError", "red"))
                    print(colored("user: " + str(user), "red"))
                    print(colored("path: " + str(path), "red"))
                    print(
                        colored(
                            "response.status_code: " + str(response.status_code), "red"
                        )
                    )
                    print(colored("status_code: " + str(status_code), "red"))
                    print(colored("response: " + str(response), "red"))
                    raise AssertionError

            if not no_login:
                logout = self.client.logout()
