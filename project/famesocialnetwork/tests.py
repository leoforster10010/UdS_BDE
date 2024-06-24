from django.test import TestCase
import random as rnd

from socialnetwork import api

# make tests deterministic:
rnd.seed(42)

from fame.models import Fame, ExpertiseAreas, FameLevels
from famesocialnetwork.library import test_paths_for_allowed_and_forbidden_users
from socialnetwork.models import (
    Posts,
    SocialNetworkUsers,
    TruthRatings,
    UserRatings,
    PostExpertiseAreasAndRatings,
)


class ViewExistsTests(TestCase):
    fixtures = ["database_dump.json"]

    def test_view_overview_exists_fm(self):
        test_paths_for_allowed_and_forbidden_users(
            self,
            paths=[
                "/",
            ],
            users_allowed="N",
            users_forbidden="",
        )


class DataConsistencyTests(TestCase):
    """Tests for the data consistency of the database in the sense whether certain constraints are met."""

    fixtures = ["database_dump.json"]

    def test_basic_fake_data(self):
        user_count = SocialNetworkUsers.objects.count()
        self.assertTrue(user_count >= 20)
        self.assertTrue(Fame.objects.count() >= user_count * 2)
        self.assertTrue(ExpertiseAreas.objects.count() >= 10)
        self.assertTrue(FameLevels.objects.count() >= 10)
        self.assertTrue(TruthRatings.objects.count() >= 8)
        self.assertTrue(UserRatings.objects.count() >= 3 * Posts.objects.count())
        self.assertTrue(
            PostExpertiseAreasAndRatings.objects.count() >= 2 * Posts.objects.count()
        )
        # no banned users in fake data to start with:
        self.assertFalse(SocialNetworkUsers.objects.filter(is_banned=True).exists())

    def test_posts_created(self):
        self.assertTrue(Posts.objects.count() >= 400)
        self.assertTrue(Posts.objects.filter(published=True).exists())
        self.assertTrue(Posts.objects.filter(published=False).exists())
        self.assertFalse(Posts.objects.filter(content=False).exists())
        self.assertFalse(Posts.objects.filter(content="").exists())

    def test_posts_rated(self):
        self.assertTrue(
            PostExpertiseAreasAndRatings.objects.filter(
                truth_rating__isnull=False
            ).exists()
        )
        self.assertTrue(
            PostExpertiseAreasAndRatings.objects.filter(
                truth_rating__isnull=True
            ).exists()
        )

        post_count = Posts.objects.count()

        self.assertTrue(PostExpertiseAreasAndRatings.objects.count() >= post_count * 2)
        self.assertTrue(UserRatings.objects.count() >= post_count * 3)

    def test_post_no_negatively_rated_posts_are_published(self):
        # no post with a negative truth rating should be published:
        self.assertFalse(
            PostExpertiseAreasAndRatings.objects.filter(
                post__published=True, truth_rating__numeric_value__lt=0
            ).exists()
        )


class StudentTasksTests(TestCase):
    fixtures = ["database_dump.json"]

    def test_post_no_negatively_rated_posts_are_published_individual(self):
        # no post with a negative truth rating should be published:

        # pick a random post with a negative truth rating:
        negative_post_rating = rnd.choice(
            PostExpertiseAreasAndRatings.objects.filter(
                truth_rating__numeric_value__lt=0,
            )
        )
        # get the content of the post:
        content = negative_post_rating.post.content

        # get a random user different from the original author:
        user = rnd.choice(
            SocialNetworkUsers.objects.filter(
                fame__fame_level__numeric_value__lt=0,
                fame__fame_level__numeric_value__gte=-100,
            ).exclude(id=negative_post_rating.post.author.id)
        )

        ret_dict, _expertise_areas, redirect_to_logout = api.submit_post(
            user, content, cites=None, replies_to=None
        )
        self.assertFalse(ret_dict["published"])
        self.assertEqual(len(_expertise_areas), 2)

    def test_T1(
        self,
    ):  # implemented and tested
        # Task 1
        # change api.submit_post to not publish posts that have an expertise area which is contained in the user’s
        # fame profile and marked negative there (independent of any truth rating determined by the magic AI for
        # this post)

        # pick a random post without truth rating:
        negative_post_rating = rnd.choice(
            PostExpertiseAreasAndRatings.objects.filter(
                truth_rating=None,
            )
        )
        # get the expertise area and content of this post:
        expertise_area = negative_post_rating.expertise_area
        # get the content of the post:
        content = negative_post_rating.post.content

        # get a random user different from the original author who has a negative fame level for this expertise area
        user = rnd.choice(
            SocialNetworkUsers.objects.filter(
                fame__expertise_area=expertise_area,
                fame__fame_level__numeric_value__lt=0,
            ).exclude(id=negative_post_rating.post.author.id)
        )

        # for this user: send a new post with the exact same content:
        # recall, that eas and truth ratings are guaranteed to be the same for the same content
        ret_dict, _expertise_areas, redirect_to_logout = api.submit_post(
            user, content, cites=None, replies_to=None
        )

        self.assertFalse(ret_dict["published"])
        self.assertEqual(len(_expertise_areas), 2)

    # Task 2
    # change api.submit_post to adjust the fame profile of the user if he/she submits a post with a negative
    # truth rating
    def test_T2a(self):  # implemented and tested
        # If the expertise area is already contained in the user’s fame profile, lower the fame to the next
        # possible level.

        # pick a random post with a negative truth rating:
        negative_post_rating = rnd.choice(
            PostExpertiseAreasAndRatings.objects.filter(
                truth_rating__numeric_value__lt=0,
            )
        )
        # get the expertise area and content of this post:
        expertise_area = negative_post_rating.expertise_area
        # get the content of the post:
        content = negative_post_rating.post.content

        # get a random user different from the original author who has a negative fame level for this expertise area
        # (which is not on the lowest fame level):
        user = rnd.choice(
            SocialNetworkUsers.objects.filter(
                fame__expertise_area=expertise_area,
                fame__fame_level__numeric_value__lt=0,
                fame__fame_level__numeric_value__gte=-100,
            ).exclude(id=negative_post_rating.post.author.id)
        )

        # for this user get the old fame for this expertise area:
        old_fame_level = Fame.objects.get(
            user=user, expertise_area=expertise_area
        ).fame_level

        # for this user: send a new post with the exact same content:
        # recall, that eas and truth ratings are guaranteed to be the same for the same content
        api.submit_post(user, content, cites=None, replies_to=None)

        # for this user: get the new fame for this expertise area:
        new_fame_level = Fame.objects.get(
            user=user, expertise_area=expertise_area
        ).fame_level

        # the new fame level for this user must be different now:
        self.assertFalse(old_fame_level == new_fame_level)

        # the new fame level for this user must actually be the next lower fame level:
        self.assertTrue(old_fame_level.get_next_lower_fame_level() == new_fame_level)

    def test_T2b(self):  # implemented and tested
        # If the expertise area is not contained, simply add an entry in the user’s fame profile with fame
        # level “Confuser”.

        # pick a random post with a negative truth rating:
        negative_post_rating = rnd.choice(
            PostExpertiseAreasAndRatings.objects.filter(
                truth_rating__numeric_value__lt=0,
            )
        )
        # get the expertise area and content of this post:
        expertise_area = negative_post_rating.expertise_area
        # get the content of the post:
        content = negative_post_rating.post.content

        # get a random user different from the original author who DOES NOT HAVE this expertise area in his/her fame
        # profile:
        all_user_ids_without_expertise_area = list(
            set(SocialNetworkUsers.objects.all().values_list("id", flat=True))
            - set(
                Fame.objects.filter(expertise_area=expertise_area).values_list(
                    "user", flat=True
                )
            )
        )

        # pick a random user from the remaining users:
        user = SocialNetworkUsers.objects.get(
            id=rnd.choice(all_user_ids_without_expertise_area)
        )

        # for this user no fame entry with this ea should exist:
        self.assertFalse(
            Fame.objects.filter(user=user, expertise_area=expertise_area).exists()
        )

        # for this user: send a new post with the exact same content:
        # recall, that eas and truth ratings are guaranteed to be the same for the same content
        api.submit_post(user, content, cites=None, replies_to=None)

        # for this user: get the newly created fame entry for this expertise area:
        new_fame_level = Fame.objects.get(
            user=user, expertise_area=expertise_area
        ).fame_level

        # the fame_level should be "Confuser":
        self.assertEqual(new_fame_level.name, "Confuser")

    def _user_is_banned_test(self, use_DRF_endpoint: bool = False):
        # If you cannot lower the existing fame level for that expertise area any further, ban the user from the
        # social network by
        # setting the field is_banned,

        # pick a random post with a negative truth rating:
        negative_post_rating = rnd.choice(
            PostExpertiseAreasAndRatings.objects.filter(
                truth_rating__numeric_value__lt=0,
            )
        )
        # get the expertise area and content of this post:
        expertise_area = negative_post_rating.expertise_area
        # get the content of the post:
        content = negative_post_rating.post.content

        # get a random user different from the original author who has a "Dangerous Bullshitter" fame level for this
        # expertise area
        user = rnd.choice(
            SocialNetworkUsers.objects.filter(
                fame__expertise_area=expertise_area,
            ).exclude(id=negative_post_rating.post.author.id)
        )
        # manipulate fame level entry for this user:
        old_fame_entry = Fame.objects.get(user=user, expertise_area=expertise_area)
        old_fame_level = old_fame_entry.fame_level
        old_fame_entry.fame_level = FameLevels.objects.get(name="Dangerous Bullshitter")
        old_fame_entry.save()

        # for this user: send a new post with the exact same content:
        # recall, that eas and truth ratings are guaranteed to be the same for the same content
        if use_DRF_endpoint:
            self.client.login(email=user.email, password="test")
            ret = self.client.post(
                "/sn/api/posts",
                {"text": content},
            )
            self.assertEqual(ret.status_code, 302)
            self.assertFalse(ret.url.endswith("timeline"))

        else:
            ret, _expertise_areas, redirect_to_logout = api.submit_post(
                user, content, cites=None, replies_to=None
            )
            self.assertTrue(redirect_to_logout)

        # for this user: get the new fame for this expertise area:
        new_fame_level = Fame.objects.get(
            user=user, expertise_area=expertise_area
        ).fame_level

        # same fame level as before:
        self.assertTrue(new_fame_level.name == "Dangerous Bullshitter")

        user_reread = SocialNetworkUsers.objects.get(id=user.id)
        self.assertFalse(user_reread.is_active)

        # restore old fame level:
        old_fame_entry.fame_level = old_fame_level
        old_fame_entry.save()

        return user

    def test_T2c_1(self):  # implemented and tested
        self._user_is_banned_test()

    def test_T2c_2(self):  # implemented and tested
        # logging out the user if he/she sends another GET request,
        # call the endpoint to check whether it logs out the user
        self._user_is_banned_test(use_DRF_endpoint=True)

    def test_T2c_3(self):  # implemented and tested
        # disallowing him/her to ever login again.
        user = self._user_is_banned_test()
        login = self.client.login(email=user.email, password="test")
        self.assertFalse(login)

    def test_T2c_4(self):  # implemented and tested
        # unpublish all her/his posts (without deleting them from the database)
        user = self._user_is_banned_test()

        # get all posts for this user:
        user_posts = Posts.objects.filter(author=user)
        for post in user_posts:
            # check whether the post is unpublished:
            self.assertFalse(post.published)

    def _test_containment(self, my_dictionary, filter_conditions, reverse=False):
        # test whether everything returned is actually contained in the database:
        test_set = set()
        for ea, value in my_dictionary.items():
            # print(ea)
            previous_fame_level_numeric = None
            previous_date_joined = None
            for v in value:
                user = v["user"]
                fame_level_numeric = v["fame_level_numeric"]
                # date_joined = user.date_joined
                # print("\t", user, ea, fame_level_numeric, date_joined)
                self.assertTrue(
                    Fame.objects.filter(
                        user=user,
                        expertise_area=ea,
                        fame_level__numeric_value=fame_level_numeric,
                    ).exists()
                )
                # sort by numeric_value (or reversed), test this:
                self.assertTrue(
                    previous_fame_level_numeric is None  # first iteration or new ea
                    or (
                        reverse
                        and (
                            previous_fame_level_numeric >= fame_level_numeric
                        )  # sort on numeric_value descending
                    )
                    or (
                        not reverse
                        and (
                            previous_fame_level_numeric <= fame_level_numeric
                        )  # sort on numeric_value ascending
                    )
                )
                # within that tie sort by date_joined (most recent first), test this:
                self.assertTrue(
                    previous_date_joined is None  # first iteration or new ea
                    or previous_fame_level_numeric != fame_level_numeric  # new fame level
                    or previous_date_joined >= user.date_joined  # tie: sort on date_joined descending
                )

                previous_date_joined = user.date_joined
                previous_fame_level_numeric = fame_level_numeric

                # add to test set for vice versa test:
                test_set.add((user, ea, fame_level_numeric))

        # vice versa: test whether everything in the database is contained in the result:
        for fame_entry in Fame.objects.filter(**filter_conditions):
            user = fame_entry.user
            ea = fame_entry.expertise_area
            fame_level_numeric = fame_entry.fame_level.numeric_value
            self.assertTrue((user, ea, fame_level_numeric) in test_set)

    def test_T3(self):  # implemented and tested
        # implement api.experts: It should return for each existing expertise area in the fame profiles a list of the
        # users having positive fame for that expertise area, the list should be ranked, i.e. users with the highest
        # fame are shown first, in case there is a tie, within that in case there is a tie, within that tie sort
        # by date_joined (most recent first)

        filter_conditions = {"fame_level__numeric_value__gt": 0}
        self._test_containment(api.experts(), filter_conditions, reverse=True)

    def test_T4(self):  # implemented and tested
        # implement api.bullshitters: It should return for each existing expertise area in the fame profiles a list
        # of the users having negative fame for that expertise area, the list should be ranked, i.e. users with the
        # lowest fame are shown first, in case there is a tie, within that tie sort by date_joined (most recent first)

        filter_conditions = {"fame_level__numeric_value__lt": 0}
        self._test_containment(api.bullshitters(), filter_conditions, reverse=False)
