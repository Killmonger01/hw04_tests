from django import forms
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='Testname')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='Test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.picture = (
            b'\x00\x80'
            b'\x80\x00'
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': 'Test_slug'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                args=[get_object_or_404(User, username='Testname')]
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.pk}'}
            ),
            'posts/create_post.html': reverse(
                'posts:post_create'
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        test_objects = response.context.get('page_obj').object_list
        expected = list(Post.objects.all())
        self.assertEqual(test_objects, expected)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug})
        )
        context_post_list = response.context.get('page_obj').object_list
        db_post_list = list(self.group.posts.all())
        self.assertQuerysetEqual(
            db_post_list,
            context_post_list,
            transform=lambda x: x
        )

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_post_edit_show_correct_context(self):
        response = (self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Testname')
        cls.group = Group.objects.create(
            title='Тестовый тайтл',
            slug='Test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовый текст{i}',
                    author=cls.user,
                    group=cls.group
                )
                for i in range(0, 13)
            ]
        )

    def test_first_page_contains(self):
        page_limit = 10
        url_names = {
            reverse('posts:index'): page_limit,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): page_limit,
            reverse(
                'posts:profile',
                args=[self.user]
            ): page_limit,
        }
        for value, expected in url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value + '?page=1')
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_second_page_contains_three_records(self):
        page_limit_second_page = 3
        url_names = {
            reverse(
                'posts:index'
            ): page_limit_second_page,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): page_limit_second_page,
            reverse(
                'posts:profile',
                args=[self.user]
            ): page_limit_second_page,
        }
        for value, expected in url_names.items():
            with self.subTest(value=value):
                response = self.client.get(value + '?page=2')
                self.assertEqual(len(response.context['page_obj']), expected)
