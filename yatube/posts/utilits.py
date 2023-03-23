from django.core.paginator import Paginator


def page_paginator(request, post_list):
    number_of_posts = 10
    paginator = Paginator(post_list, number_of_posts)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
