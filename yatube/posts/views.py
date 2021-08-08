from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from yatube.settings import POSTS_ON_PAGE
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def paginator_in_view(request, post_list):
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page = paginator_in_view(request, post_list)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug=''):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page = paginator_in_view(request, post_list)
    context = {'group': group, 'page': page}
    return render(request, 'posts/group.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page = paginator_in_view(request, post_list)
    following = False
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    context = {'author': author, 'page': page, 'following': following}
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    if request.user.is_authenticated:
        return add_comment(request, username, post_id)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = Comment.objects.filter(post__id=post_id)
    context = {'post': post, 'comments': comments, 'form': CommentForm()}
    return render(request, 'posts/post.html', context)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return render(
            request, 'posts/post.html', {'post': post,
                                         'comments': post.comments.all(),
                                         'form': form}
        )
    instance = form.save(commit=False)
    instance.author = request.user
    instance.post = post
    instance.save()
    return redirect('posts:post', username, post_id)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES)
    if not form.is_valid():
        context = {'form': form, 'is_edit': False}
        return render(request, 'posts/new.html', context)
    instance = form.save(commit=False)
    instance.author = request.user
    instance.save()
    return redirect('posts:index')


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    if post.author != request.user:
        return redirect('posts:index')
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if not form.is_valid():
        context = {'form': form, 'is_edit': True}
        return render(request, 'posts/new.html', context)
    form.save()
    return redirect('posts:post', username, post_id)


@login_required
def follow_index(request):
    authors = [i.author for i in Follow.objects.filter(user=request.user)]
    post_list = Post.objects.filter(author__in=authors)
    page = paginator_in_view(request, post_list)
    return render(request, 'posts/follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    lock_repeat = request.user.username + username
    if request.user.username != username and not Follow.objects.filter(
        lock_repeat=lock_repeat
    ).exists():
        Follow.objects.create(user=request.user,
                              author=User.objects.get(username=username),
                              lock_repeat=lock_repeat)
    return profile(request, username)


@login_required
def profile_unfollow(request, username):
    lock_repeat = request.user.username + username
    if Follow.objects.filter(lock_repeat=lock_repeat).exists():
        Follow.objects.get(user=request.user,
                           author=User.objects.get(username=username)).delete()
    return profile(request, username)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
