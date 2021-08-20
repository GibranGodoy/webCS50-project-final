from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("signin", views.signin_view, name="signin"),
    path("", views.index, name="index"),
    path("my_blogs", views.my_blogs, name="my_blogs"),
    # path("my_blogs", views.MyPosts.as_view(), name="my_blogs"),
    # path("available_blogs", views.available_blogs, name="available_blogs"),
    path("available_blogs", views.PostList.as_view(), name="available_blogs"),
    # path("available_blogs/<slug:slug>/", views.PostDetail.as_view(), name='post_detail'),
    path("new_post/", views.newPost, name="new_post"),
    path("available_blogs/<slug:slug>/", views.post_detail, name="post_detail"),
    path("my_blogs/<slug:slug>/", views.mypost_detail, name="mypost_detail"),
    path("my_blogs/edit/<slug:slug>/", views.mypost_edit, name="mypost_edit"),
    path("search_post/", views.Search, name="search_post"),
    path("my_blogs/delete/<slug:slug>/", views.mypost_delete, name="mypost_delete"),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)