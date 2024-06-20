from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from socialnetwork.api import _get_social_network_user


@require_http_methods(["GET"])
@login_required
def home(request):
    return render(request, "index.html")


class MyLoginView(LoginView):
    def form_valid(self, form):

        #########################
        # add your code here
        #########################


        response = super().form_valid(form)
        return response


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("auth:login")
