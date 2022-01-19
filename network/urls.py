
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("profile/<str:name>", views.profile, name="profile"),
    path("follow/<int:name_id>", views.follow, name="follow"),
    path("unfollow/<int:name_id>", views.unfollow, name="unfollow"),
    path("following", views.following, name="following"),
    path("like/<int:post_id>", views.like, name="like"),
    path("likers/<int:post_id>", views.likers, name="likers"),
    path("comment/<int:post_id>", views.comment, name="comment"),
]
