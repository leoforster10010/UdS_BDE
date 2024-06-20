import random as rnd

from fame.models import ExpertiseAreas
import hashlib

rnd.seed(42)


def classify_into_expertise_areas_and_check_for_bullshit(content: str):
    """Classify the given content into expertise areas."""

    # in the absence of a real text classifier, we just randomly assign expertise areas and truth ratings:
    # the random engine is initialized with a hash of the content to make the results deterministic for testing purposes

    # it is important to note that this is not how a real classifier would work! This is just a mockup!

    # Also note that we simulate a real classifier in the sense that sometimes we only return the expertise areas
    # without any truth ratings. This is to simulate the fact that a real classifier might not be able to classify
    # the content into truth ratings.

    # also note that in a real system, this could be improved by integrating human moderation and feedback loops

    # compute a seed based on the content:
    seed = int(hashlib.md5(content.encode()).hexdigest(), 16)

    # get a local random engine to make the results deterministic for testing purposes:
    lre = rnd.Random(seed)

    def get_truth_ratings(is_positive: bool):
        from socialnetwork.models import TruthRatings

        if is_positive:
            return lre.choice(TruthRatings.objects.filter(numeric_value__gt=0))
        else:  # is negative
            return lre.choice(TruthRatings.objects.filter(numeric_value__lt=0))

    return [
        {
            "expertise_area": s,
            "truth_rating": (
                None
                if lre.random() < 0.2
                else (  # sometimes the AI cannot determine the truth rating
                    get_truth_ratings(True)
                    if lre.random() < 0.8
                    else get_truth_ratings(False)
                )
            ),
        }
        for s in lre.sample(list(ExpertiseAreas.objects.all()), 2)
    ]
