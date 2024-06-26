from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from fame.models import Fame
from fame.serializers import FameSerializer
from socialnetwork import api
from socialnetwork.api import _get_social_network_user
from socialnetwork.models import SocialNetworkUsers


@require_http_methods(["GET"])
@login_required
def fame_list(request):
    # try to get the user from the request parameters:
    userid = request.GET.get("userid", None)
    user = None
    if userid is None:
        user = _get_social_network_user(request.user)
    else:
        try:
            user = SocialNetworkUsers.objects.get(id=userid)
        except ValueError:
            pass

    user, fame = api.fame(user)
    context = {
        "fame": FameSerializer(fame, many=True).data,
        "user": user if user else "",
    }
    return render(request, "fame.html", context=context)

# New function for displaying the Expert List
# I decided to omit the authentication because why not :-)
@require_http_methods(["GET"])
def experts_list(request):
    # Just call Leos function (T3)
    experts_dict = api.experts()
    # return the rendered HTML website, given the template experts.html and the context of the experts_dict
    return render(request, "experts.html", context={"experts": experts_dict})

@require_http_methods(["GET"])
def bullshitters_list(request):
    # Call Leos function (T4)
    bullshitters_dict = api.bullshitters()
    # return the rendered HTML website, given the template bullshitters.html and the context of the bullshitters_dict
    return render(request, "bullshitters.html", context={"bullshitters": bullshitters_dict})
