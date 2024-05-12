
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("u/<int:id>",views.profile,name="profile"),
    path("following",views.following,name="following"),
    path("p/<int:id>",views.post_details,name="post_details")
]
