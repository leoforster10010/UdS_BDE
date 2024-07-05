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
@login_required
def experts_list(request):
    # Just call Leos function (T3)
    experts_dict = api.experts()
    # return the rendered HTML website, given the template experts.html and the context of the experts_dict
    # in the context the key is the name of the variable in the html page, and the value is our object
    return render(request, "experts.html", context={"experts": experts_dict})

@require_http_methods(["GET"])
@login_required
def bullshitters_list(request):
    # Call Leos function (T4)
    bullshitters_dict = api.bullshitters()
    # return the rendered HTML website, given the template bullshitters.html and the context of the bullshitters_dict
    # in the context the key is the name of the variable in the html page, and the value is our object
    return render(request, "bullshitters.html", context={"bullshitters": bullshitters_dict})
    
# new function for following
@require_http_methods(["POST"])
@login_required
def follow(request, username):
    """define the two users to use the predefined follow function"""
    follower = request.user
    followed = api._get_social_network_user(username)
    """No output, because we only update followed"""
    result = follow(follower, followed)

# new function for unfollowing
@require_http_methods(["POST"])
@login_required
def unfollow(request, username):
    """define the two users to use the predefined unfollow function"""
    follower = request.user
    followed = api._get_social_network_user(username)
    """No output, because we only update unfollowed"""
    result = unfollow(follower, followed)
