from django.test import TestCase

from famesocialnetwork.library import test_paths_for_allowed_and_forbidden_users


class ViewExistsTests(TestCase):
    fixtures = ["database_dump.json"]

    def setUp(self):
        pass

    def test_view_overview_exists(self):
        test_paths_for_allowed_and_forbidden_users(
            self,
            paths=[
                "/sn/api/posts",
                "/sn/html/timeline",
                "/sn/html/timeline?userid=13",
            ],
            users_allowed="P",
            users_forbidden="N",
        )
