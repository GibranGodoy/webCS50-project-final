from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect 
from django.urls import reverse
from django.views import generic
from .models import Post
from .forms import CommentForm
import django_filters
from django.core import serializers
from django.utils.text import slugify

# Create your views here.

# admin=User.objects.filter(is_superuser=True)
# if admin.count()==0:
#     admin=User.objects.create_user("admin", "admin@admin.com", "admin")
#     admin.is_superuser=True
#     admin.is_staff=True
#     admin.save()

def index(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    context={
        "user": request.user,
    }
    return render(request, "index.html", context)

def login_view(request):
    if request.method=="GET":
        return render(request, "login.html")
    username = request.POST["username"]
    password = request.POST["password"]
    remember_me=request.POST.get("remember_me", None)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        if not remember_me:
            request.session.set_expiry(0)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "login.html", {"message": "Invalid credentials."})

    # remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # if not self.cleaned_data.get('remember_me'):
    #     self.request.session.set_expiry(0)

    return render(request, "index.html")

def signin_view(request):
    if request.method=="POST":
        username=request.POST["username"]
        email=request.POST["email"]
        password=request.POST["password"]
        confirm_password=request.POST["confirm_password"]
        if User.objects.filter(username=username).exists():
            return render(request, "signin.html", {"message": "User already exists"})
        if not password==confirm_password:
            return render(request, "signin.html", {"message": "Passwords don't match"})
        user=User.objects.create_user(username, email, password)
        user.save()
        return render(request, "login.html", {"message": "Signed up"})
    return render(request, "signin.html")

def logout_view(request):
    logout(request)
    return render(request, "login.html", {"message": "Logged out"})

def my_blogs(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    template_name='my_blogs.html'
    userID=request.user.id
    post=Post.objects.filter(author=userID).order_by('-created_on')

    return render(request, template_name, {"post": post})

def available_blogs(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    return render(request, "available_blogs.html")

def Search(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    template_name='search_blogs.html'
    if request.method=="POST":
        data=request.POST['search']
        if not data.replace(" ",""):
            return render(request, template_name, {"message": "Invalid search"})

        post=Post.objects.filter(title__contains=data, status=1).order_by('-created_on')
        if len(post)==0:
            return render(request, template_name, {"message": "No such post with that name"})
        return render(request, template_name, {"post": post})
    return HttpResponseRedirect(reverse("index"))


def post_detail(request, slug):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    template_name = 'post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True).order_by("-created_on")
    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, template_name, {"post": post,
                                           "comments": comments,
                                           "new_comment": new_comment,
                                           "comment_form": comment_form})

def mypost_detail(request, slug):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    template_name = 'mypost_detail.html'
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True).order_by("-created_on")
    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, template_name, {"post": post,
                                           "comments": comments,
                                           "new_comment": new_comment,
                                           "comment_form": comment_form})

def mypost_edit(request, slug):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    template_name='mypost_edit.html'
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        title=request.POST['post']
        content=request.POST['content']
        status=request.POST['status']
        post.title=title
        post.content=content
        post.status=status
        post.save()
        comments = post.comments.filter(active=True).order_by("-created_on")
        new_comment = None
        comment_form = CommentForm()
        return render(request, 'mypost_detail.html', {"post": post,
                                                      "comments": comments,
                                                      "new_comment": new_comment,
                                                      "comment_form": comment_form})
    return render(request, template_name, {"post": post})

def newPost(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    user=request.user
    if request.method == 'GET':
        return render(request, 'new_post.html')
    if request.method == 'POST':
        title=request.POST['post']
        slug=slugify(title)
        username=user.username
        author=User.objects.get(username=username)
        content=request.POST['content']
        status=request.POST['status']
        new_post=Post.objects.create(title=title, slug=slug, author=author, content=content, status=status)
        new_post.save()
        post=new_post
        comments = post.comments.filter(active=True).order_by("-created_on")
        new_comment = None
        comment_form = CommentForm()
        return render(request, 'mypost_detail.html', {"post": post,
                                                      "comments": comments,
                                                      "new_comment": new_comment,
                                                      "comment_form": comment_form})
    
def mypost_delete(request, slug):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message": None})
    Post.objects.filter(slug=slug).delete()
    return render(request, 'index.html', {"message": "The post has been deleted"})

class PostList(generic.ListView):
    queryset=Post.objects.filter(status=1).order_by('-created_on')
    template_name='available_blogs.html'
    paginate_by=3

class MyPosts(generic.ListView):
    queryset=Post.objects.filter(status=1).order_by('-created_on')
    template_name='my_blogs.html'
    paginate_by=3

# class PostDetail(generic.DetailView):
#     model=Post
#     template_name='post_detail.html'