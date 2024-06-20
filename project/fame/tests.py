from django.test import TestCase
from django.urls import reverse
from rest_framework.utils import json

from fame.models import ExpertiseAreas, Fame, FameLevels
from famesocialnetwork.library import test_paths_for_allowed_and_forbidden_users


# Create your tests here.
class ViewExistsTests(TestCase):
    fixtures = ["database_dump.json"]

    def TODO_test_post(self):
        data = {
            "label": "bla",
            "parent_expertise_area": None,
        }

        ret = self.client.post(
            reverse("fame:expertise_areas"),
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(ret.status_code, 201)
        self.assertTrue(ExpertiseAreas.objects.get(label="bla") is not None)
        self.assertTrue(ExpertiseAreas.objects.count() == 1)

    def test_view_overview_exists_fm(self):
        test_paths_for_allowed_and_forbidden_users(
            self,
            paths=[
                "/fame/api/fame",
                "/fame/api/fame",
                "/fame/api/fame?userid=21",
            ],
            users_allowed="P",
            users_forbidden="N",
        )


class ModelTests(TestCase):
    fixtures = ["database_dump.json"]

    def test_fame_level_increase(self):
        fl = FameLevels.objects.get(
            name="Dangerous Bullshitter"
        ).get_next_higher_fame_level()
        self.assertTrue(fl.name == "Serious Bullshitter")

        fl = FameLevels.objects.get(
            name="Serious Bullshitter"
        ).get_next_higher_fame_level()
        self.assertTrue(fl.name == "Bullshitter")

        fl = FameLevels.objects.get(name="Newbie").get_next_higher_fame_level()
        self.assertTrue(fl.name == "Knowledgeable")

        with self.assertRaises(ValueError):
            fl = FameLevels.objects.get(name="Jedi").get_next_higher_fame_level()

    def test_fame_level_decrease(self):
        fl = FameLevels.objects.get(
            name="Serious Bullshitter"
        ).get_next_lower_fame_level()
        self.assertTrue(fl.name == "Dangerous Bullshitter")

        fl = FameLevels.objects.get(name="Bullshitter").get_next_lower_fame_level()
        self.assertTrue(fl.name == "Serious Bullshitter")

        fl = FameLevels.objects.get(name="Knowledgeable").get_next_lower_fame_level()
        self.assertTrue(fl.name == "Newbie")

        with self.assertRaises(ValueError):
            fl = FameLevels.objects.get(
                name="Dangerous Bullshitter"
            ).get_next_lower_fame_level()
