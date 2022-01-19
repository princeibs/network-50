from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
from network.models import User


def index(request):
    posts = Post.objects.all().order_by("-timestamp").all()
    paginator = Paginator(posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        "posts": posts,
    }
    return render(request, "network/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            follow = Follow.objects.create(name=user)
            follow.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url="login")
def new_post(request):
    if request.method == "POST":
        name = request.user
        post = request.POST["post"]

        # Save the new post
        new_post = Post.objects.create(name=name, post=post)
        new_post.save()

        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, "network/new_post.html")

@login_required(login_url="login")
def profile(request, name):
    name = User.objects.get(username=name)
    my_posts = Post.objects.filter(name=name.id).order_by("-timestamp").all()
    no_of_posts = Post.objects.filter(name=name.id).count()
    followers = Follow.objects.get(name=name).followers.count()
    following = Follow.objects.get(name=name).follows.count()
    is_me = False
    follow = True

    # Checks if this is the logged in user's profile
    if request.user == name:
        is_me = True

    # Checks if the logged in user follows this user
    try:
        Follow.objects.get(name=request.user, follows=name.id)
    except Follow.DoesNotExist:
        follow = False

    paginator = Paginator(my_posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        "name": name,
        "posts": posts,
        "no_of_posts": no_of_posts,
        "followers": followers,
        "following": following,
        "is_me": is_me,
        "follow": follow,
    }
    return render(request, "network/profile_page.html", context)


@login_required(login_url="login")
def follow(request, name_id):
    me = request.user
    name = User.objects.get(id=name_id)

    followers = Follow.objects.get(name=name.id).followers.add(me)
    follows = Follow.objects.get(name=request.user).follows.add(name.id)
    return HttpResponseRedirect(reverse('profile', args=(name.username,)))


@login_required(login_url="login")
def unfollow(request, name_id):
    me = request.user
    name = User.objects.get(id=name_id)

    followers = Follow.objects.get(name=name.id).followers.remove(me)
    follows = Follow.objects.get(name=request.user).follows.remove(name.id)
    return HttpResponseRedirect(reverse('profile', args=(name.username,)))


@login_required(login_url="login")
def following(request):
    # Get all of people the user's follow and store in a list
    user = request.user
    followings = user.followers_all.all()
    names = [following.name for following in followings]

    # Filter posts according to the user's following
    posts = Post.objects.filter(name__in=names).order_by("-timestamp").all()
    paginator = Paginator(posts, 10) # Show 10 contacts per page.
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        "posts": posts,
    }
    return render(request, "network/following.html", context)

def likers(request, post_id):
    post = Post.objects.get(pk=post_id).likes.all
    context = {
        "likers": post,
    }
    return render(request, "network/likers.html", context)

@csrf_exempt
def comment(request, post_id):
    me = request.user
    post = Post.objects.get(pk=post_id)
    if request.method == "POST":
        # Get the data sent from webpage and create a new comment
        data = json.loads(request.body)
        print(data["comment"])
        new_comment = Comment.objects.create(name=me, comment=data["comment"])
        new_comment.save()
        post.comments.add(new_comment)
        post.save()
        # Returns the comment object
        context = {
            "name": me.username,
            "comment": new_comment.comment,
            "timestamp": new_comment.timestamp,
        }
        return JsonResponse(context, status=201)

@csrf_exempt
@login_required(login_url="login")
def like(request, post_id):
    me = request.user
    post = Post.objects.get(pk=post_id)
    liked = me in post.likes.all()

    # Like post
    if liked:
        post.likes.remove(me)

    # Unlike post
    else:
        post.likes.add(me)

    post.save()
    context = {
        "liked": liked,
        "count": Post.objects.get(pk=post_id).likes.count()
    }
    return JsonResponse(context, status=201)

@csrf_exempt
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        # Get the edited post and replace the original post with it
        data = json.loads(request.body)
        post.post = data['text']
        post.save()
        return JsonResponse({'new_post': data['text']}, status=201)

    context = {
        "post": post.post,
    }
    return JsonResponse(context, status=201)
