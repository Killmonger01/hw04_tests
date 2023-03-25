from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create_user(username='Testname1')
        cls.post = Post.objects.create(text='тестовый текст',
                                       author=cls.author_user)
        cls.group = Group.objects.create(title='тестовый заголовок',
                                         slug='test-slug',
                                         description='тестовый дескриптор')

    def setUp(self):
        self.author = Client()
        self.author.force_login(self.author_user)

    def test_all_users_page(self):
        pages = {'homepage': '/',
                 'group': f'/group/{self.group.slug}/',
                 'profile': f'/profile/{self.post.author.get_username()}/',
                 'detail': f'/posts/{self.post.pk}/'}
        for field, expected_value in pages.items():
            with self.subTest(field=field):
                response = self.client.get(expected_value)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_only_auth_page(self):
        pages = {
            'create': '/create/',
            'post_edit': f'/posts/{self.post.pk}/edit/'
        }
        for field, expected_value in pages.items():
            with self.subTest(field=field):
                response = self.author.get(expected_value)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author.get_username()}/': ('posts/'
                                                             'profile.html'),
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author.get(address)
                self.assertTemplateUsed(response, template)
