from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect,JsonResponse 
from django.shortcuts import render ,redirect
from django.urls import reverse
from django.core.paginator import Paginator
from .models import User,Post,Follow,Like
from django.views.decorators.csrf import csrf_exempt
import json


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    p = Paginator(posts,10)
    if request.method == "POST" :
        text = request.POST["t"]
        if text :
            Post.objects.create(user=request.user,text=text)
        return redirect("/")
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    return render(request, "network/index.html",{"posts":page_obj.object_list,'page_obj': page_obj})

@login_required(login_url="/login")
def following(request):
    if request.method == "POST" :
        text = request.POST["t"]
        if text :
            Post.objects.create(user=request.user,text=text)
            return redirect("/")
        
    posts = []
    for f in request.user.following.all():
        posts.extend(f.followed.posts.all())
    posts.sort(reverse=True,key=get_timestamp)
    p = Paginator(posts,10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    return render(request, "network/following.html",{"posts":page_obj.object_list,'page_obj': page_obj})

def profile(request,id):
    user = User.objects.get(pk=id)
    posts = user.posts.all().order_by("-timestamp")
    p = Paginator(posts,10)
    page_number = request.GET.get('page')
    page_obj = p.get_page(page_number)
    
    if request.method == "POST" : 
        posts = user.posts.all().order_by("-timestamp")
        if "fo" in request.POST :
            if len(Follow.objects.filter(follower=request.user,followed=user)) != 0 :
                return render(request,"network/profile.html",{"user":user,"posts":user.posts.all().order_by("-timestamp"),"following_list":following_list})
            f = Follow.objects.create(follower=request.user,followed=user)
            f.save()
            fs = request.user.following.all()
            following_list = []
            for i in fs :
                following_list.append(i.followed.id)
            return render(request,"network/profile.html",{"user":user,"posts":page_obj.object_list,"following_list":following_list,'page_obj': page_obj})
        elif "un" in request.POST :
            f = Follow.objects.get(follower=request.user,followed=user)
            f.delete()
            fs = request.user.following.all()
            following_list = []
            for i in fs :
                following_list.append(i.followed.id)
            return render(request,"network/profile.html",{"user":user,"posts":page_obj.object_list,"following_list":following_list,'page_obj': page_obj})
    fs = request.user.following.all()
    following_list = []
    for i in fs :
        following_list.append(i.followed.id)
    return render(request,"network/profile.html",{"user":user,"posts":page_obj.object_list,"following_list":following_list,'page_obj': page_obj})

def get_timestamp(obj):
    return obj.timestamp

def serilize(id):
        post = Post.objects.get(pk=id)
        return {
            "user" : post.user.username,
            "text" : post.text,
            "timestamp" : post.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes" : post.likes,
        }
@login_required(login_url="/login")
@csrf_exempt
def post_details(request,id):
    post = Post.objects.get(pk=id)
    if request.method == "GET" :
        return JsonResponse(serilize(id))
    elif request.method == "PUT":
        body = json.loads(request.body)
        if body.get("liked") != None : 
            if len(Like.objects.filter(post=post,user=request.user)) == 0  :
                post.likes += 1
                Like.objects.create(post=post,user=request.user)
                post.save()
                return JsonResponse({"message" : "post liked"}, status=201)
            elif len(Like.objects.filter(post=post,user=request.user)) != 0  :
                post.likes -= 1
                l = Like.objects.filter(post=post,user=request.user)
                l.delete()
                post.save()
                return JsonResponse({"message" : "post unliked"}, status=201)
        elif body.get("text") != None : 
            post.text = body["text"]
            post.save()
            return JsonResponse({"text" : f"{post.text}"}, safe=False)
    else : return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


    

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

@login_required(login_url="/login")
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
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
