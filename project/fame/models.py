import random as rnd

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property


rnd.seed(42)


class ExpertiseAreas(models.Model):
    """Taxonomy of expertise area of a user."""

    label = models.CharField(max_length=255)
    parent_expertise_area = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        unique_together = ("label", "parent_expertise_area")
        db_table = "expertise_areas"

    def __str__(self):
        return self.label


class FameUsers(AbstractUser):
    """Users of the fame application."""

    email = models.EmailField(unique=True)
    expertise_area = models.ManyToManyField(
        ExpertiseAreas, related_name="fame_of", through="Fame"
    )

    # Use email as the username field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @cached_property
    def username(self):
        return self.email

    class Meta:
        db_table = "fame_users"


class FameLevels(models.Model):
    """Possible levels of expertise (aka fame) in an expertise area."""

    name = models.CharField(max_length=42, unique=True)
    numeric_value = models.IntegerField(null=False)

    def get_next_lower_fame_level(self):
        next_lower_fame = (
            FameLevels.objects.filter(numeric_value__lt=self.numeric_value)
            .order_by("-numeric_value")
            .first()
        )
        if next_lower_fame:
            return next_lower_fame
        else:
            raise ValueError(
                "Cannot lower fame level any further. Fame level is unchanged."
            )

    def get_next_higher_fame_level(self):
        next_higher_fame = (
            FameLevels.objects.filter(numeric_value__gt=self.numeric_value)
            .order_by("numeric_value")
            .first()
        )
        if next_higher_fame:
            return next_higher_fame
        else:
            raise ValueError(
                "Cannot increase fame level any further. Fame level is unchanged."
            )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "fame_levels"


class Fame(models.Model):
    """Fame of a user in a specific expertise area.
    intermediary table between FameUsers and ExpertiseAreas.
    """

    user = models.ForeignKey(FameUsers, on_delete=models.CASCADE)
    expertise_area = models.ForeignKey(ExpertiseAreas, on_delete=models.CASCADE)
    fame_level = models.ForeignKey(FameLevels, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "expertise_area")
        ordering = [
            "-fame_level__numeric_value",
        ]

        db_table = "fame"
