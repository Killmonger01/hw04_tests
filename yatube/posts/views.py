from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt


from .models import Post, Group, User
from .forms import PostForm
from .utilits import page_paginator


def index(request):
    post_list = Post.objects.all()
    page_obj = page_paginator(request=request, post_list=post_list)
    context = {'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    page_obj = page_paginator(request=request, post_list=post_list)
    context = {'group': group,
               'page_obj': page_obj}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    count_of_username = Post.objects.filter(author=author).count()
    post_list = Post.objects.filter(author=author)
    page_obj = page_paginator(request=request, post_list=post_list)
    context = {'count_of_username': count_of_username,
               'page_obj': page_obj,
               'author': author}

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.filter(author=post.author).count()
    context = {'post': post,
               'post_count': post_count}

    return render(request, 'posts/post_detail.html', context)


@login_required
@csrf_exempt
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {'form': form, 'is_edit': False}
    return render(request, 'posts/create_post.html', context)


@login_required
@csrf_exempt
def post_edit(request, post_id):
    item = Post.objects.select_related('group')
    post = get_object_or_404(item, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if post.author != request.user:
        return redirect('posts:index')
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {'form': form, 'is_edit': True}
    return render(request, 'posts/create_post.html', context)
