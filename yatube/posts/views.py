from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from yatube.settings import POSTS_ON_PAGE
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def paginator_in_view(request, post_list):
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    page = paginator_in_view(request, Post.objects.all())
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page = paginator_in_view(request, group.posts.all())
    context = {'group': group, 'page': page}
    return render(request, 'posts/group.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    page = paginator_in_view(request, author.posts.all())
    following = (
        request.user.is_authenticated
        and request.user.username != username
        and author.following.filter(user=request.user).exists())
    context = {'author': author, 'page': page, 'following': following}
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    if request.user.is_authenticated:
        return add_comment(request, username, post_id)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    context = {'post': post, 'form': CommentForm()}
    return render(request, 'posts/post.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        context = {'post': post, 'form': form}
        return render(request, 'posts/post.html', context)
    instance = form.save(commit=False)
    instance.author = request.user
    instance.post = post
    instance.save()
    return redirect('posts:post', username, post_id)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        context = {'form': form, 'is_edit': False}
        return render(request, 'posts/new.html', context)
    instance = form.save(commit=False)
    instance.author = request.user
    instance.save()
    return redirect('posts:index')


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect('posts:index')
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if not form.is_valid():
        context = {'form': form, 'is_edit': True, 'post': post}
        return render(request, 'posts/new.html', context)
    form.save()
    return redirect('posts:post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page = paginator_in_view(request, post_list)
    return render(request, 'posts/follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    if request.user.username != username:
        author = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author__username=username).delete()
    return redirect('posts:profile', username)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
