from rest_framework import serializers

from fame.models import ExpertiseAreas, FameUsers, Fame


class FameUsersSerializer(serializers.ModelSerializer):
    fame = serializers.SerializerMethodField()

    class Meta:
        model = FameUsers
        fields = ["email", "fame"]

    def get_fame(self, fame_user: FameUsers):
        ret = {}
        return ret


class ExpertiseAreasSerializer(serializers.ModelSerializer):
    parent_expertise_area = serializers.SerializerMethodField()

    class Meta:
        model = ExpertiseAreas
        fields = ["label", "parent_expertise_area"]

    def get_parent_expertise_area(self, expertise_area: ExpertiseAreas):
        if expertise_area.parent_expertise_area is None:
            return None
        # recursion up to the root expertise area:
        return ExpertiseAreasSerializer(expertise_area.parent_expertise_area).data


class FameSerializer(serializers.ModelSerializer):

    expertise_area = ExpertiseAreasSerializer()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Fame
        fields = ["user", "expertise_area", "score"]

    def get_score(self, fame: Fame):
        return {
            "name": fame.fame_level.name,
            "numeric": fame.fame_level.numeric_value,
        }
