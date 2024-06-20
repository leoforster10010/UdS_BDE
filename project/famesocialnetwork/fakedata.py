import random as rnd

from fame.models import Fame, FameLevels
from socialnetwork import api
from socialnetwork.models import TruthRatings

# make fake data generation deterministic:
rnd.seed(42)


def create_fake_data():
    from socialnetwork.models import SocialNetworkUsers, Posts, ExpertiseAreas
    from faker import Faker
    import random

    fake = Faker()

    # Create users:
    for _ in range(20):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"

        user = SocialNetworkUsers.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password("test")
        user.save()

    user = SocialNetworkUsers.objects.create(
        email="a@b.de",
        first_name="Tom",
        last_name="Petersson",
    )
    user.set_password("test")
    user.save()

    # create followers:
    for user in SocialNetworkUsers.objects.all():
        # create followers for this user:
        sample = random.sample(
            list(SocialNetworkUsers.objects.all().exclude(id=user.id)), 7
        )
        for u in sample:
            user.follows.add(u)

    # Create expertise areas:
    ExpertiseAreas.objects.create(label="Computer Science")
    ExpertiseAreas.objects.create(label="Sports")
    ExpertiseAreas.objects.create(label="Science")
    ExpertiseAreas.objects.create(
        label="Natural Science",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Science"),
    )
    ExpertiseAreas.objects.create(label="Sheep Breeding")
    ExpertiseAreas.objects.create(label="Wine Tasting")
    ExpertiseAreas.objects.create(label="Mathematics")
    ExpertiseAreas.objects.create(
        label="Gaming", parent_expertise_area=ExpertiseAreas.objects.get(label="Sports")
    )
    ExpertiseAreas.objects.create(
        label="Soccer", parent_expertise_area=ExpertiseAreas.objects.get(label="Sports")
    )
    ExpertiseAreas.objects.create(
        label="Foosball",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Sports"),
    )
    ExpertiseAreas.objects.create(
        label="Basketball",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Sports"),
    )
    ExpertiseAreas.objects.create(
        label="Tennis", parent_expertise_area=ExpertiseAreas.objects.get(label="Sports")
    )
    ExpertiseAreas.objects.create(
        label="Physics",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Natural Science"),
    )
    ExpertiseAreas.objects.create(
        label="Quantum Physics",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Physics"),
    )
    ExpertiseAreas.objects.create(
        label="Chemistry",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Natural Science"),
    )
    ExpertiseAreas.objects.create(
        label="Wind surfing",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Sports"),
    )
    ExpertiseAreas.objects.create(
        label="Couch surfing",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Sports"),
    )
    ExpertiseAreas.objects.create(
        label="AI",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Computer Science"),
    )
    ExpertiseAreas.objects.create(
        label="ML",
        parent_expertise_area=ExpertiseAreas.objects.get(label="Computer Science"),
    )

    TruthRatings.objects.create(name="Utter Bullshit", numeric_value=-3)
    TruthRatings.objects.create(name="Partial Bullshit", numeric_value=-2)
    TruthRatings.objects.create(name="Misleading", numeric_value=-1)
    TruthRatings.objects.create(name="Neutral", numeric_value=0)
    TruthRatings.objects.create(name="Not rated", numeric_value=0)
    TruthRatings.objects.create(name="Mostly True", numeric_value=1)
    TruthRatings.objects.create(name="Completely True", numeric_value=2)
    TruthRatings.objects.create(name="Insightful", numeric_value=3)

    FameLevels.objects.create(name="Jedi", numeric_value=1000)
    FameLevels.objects.create(name="Wizard", numeric_value=300)
    FameLevels.objects.create(name="Super Pro", numeric_value=100)
    FameLevels.objects.create(name="Pro", numeric_value=80)
    FameLevels.objects.create(name="Knowledgeable", numeric_value=40)
    FameLevels.objects.create(name="Newbie", numeric_value=10)
    FameLevels.objects.create(name="Zero", numeric_value=0)
    FameLevels.objects.create(name="Confuser", numeric_value=-10)
    FameLevels.objects.create(name="Botcher", numeric_value=-40)
    FameLevels.objects.create(name="Liar", numeric_value=-80)
    FameLevels.objects.create(name="Bullshitter", numeric_value=-100)
    FameLevels.objects.create(name="Serious Bullshitter", numeric_value=-300)
    FameLevels.objects.create(name="Dangerous Bullshitter", numeric_value=-1000)

    # Create fame:
    for user in SocialNetworkUsers.objects.all():
        for expertise in rnd.sample(list(ExpertiseAreas.objects.all()), 15):
            Fame.objects.create(
                user=user,
                expertise_area=expertise,
                fame_level=rnd.choice(
                    FameLevels.objects.filter(numeric_value__gte=-50)
                ),
            )

    # submit posts through API:
    for _ in range(400):
        # call the API:
        api.submit_post(
            user=random.choice(SocialNetworkUsers.objects.all()),
            content=fake.text().strip(),
            cites=(
                random.choice(Posts.objects.all())
                if Posts.objects.all().count() > 0
                else None
            ),
            replies_to=(
                random.choice(Posts.objects.all())
                if Posts.objects.all().count() > 0 and rnd.randint(0, 5) == 0
                else None
            ),
        )

    # Create ratings:
    for post in Posts.objects.all():
        for user in rnd.sample(list(SocialNetworkUsers.objects.all()), 3):
            post.user_ratings.add(
                user,
                through_defaults={
                    "type": random.choice(["A", "L", "D"]),
                    "score": rnd.randint(0, 15),
                },
            )
