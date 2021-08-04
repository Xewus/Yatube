from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Group, Post, User


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.urls_templates_guest = {
            reverse('about:author'): 'author.html',
            reverse('about:tech'): 'tech.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group', kwargs={
                'slug': 'test_group'}): 'posts/group.html',
            reverse('posts:profile', kwargs={
                'username': 'User'}): 'posts/profile.html',
            reverse('posts:post', kwargs={
                    'username': 'User', 'post_id': 1}): 'posts/post.html',
        }
        cls.urls_templates_user = {
            reverse('posts:new_post'): 'posts/new.html'
        }
        cls.urls_templates = {
            **cls.urls_templates_guest, **cls.urls_templates_user}

        cls.user = User.objects.create(username='User')
        Group.objects.create(title='Test group',
                             description='Test description',
                             slug='test_group')
        Post.objects.create(text='Test text', author=cls.user)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Method_User')
        self.auhtorized_client = Client()
        self.auhtorized_client.force_login(self.user)

    def test_pages_any_user(self):
        for url in URLTests.urls_templates_guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonim_user(self):
        for url in URLTests.urls_templates_user:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response, '/auth/login/?next=/new/', HTTPStatus.FOUND)

    def test_pages_for_authorized_client(self):
        for url in URLTests.urls_templates:
            with self.subTest(url=url):
                response = self.auhtorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_forbidden_page(self):
        post_author = Client()
        post_author.force_login(URLTests.user)
        forbidden_url = reverse('posts:post_edit', kwargs={
            'username': 'User', 'post_id': 1})

        response = self.guest_client.get(forbidden_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.auhtorized_client.get(forbidden_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = post_author.get(forbidden_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_utl_match_template(self):
        urls_templates = {**URLTests.urls_templates,
                          **{'zzzzzz/': 'misc/404.html'}}
        for url, template in urls_templates.items():
            with self.subTest(url=url):
                response = self.auhtorized_client.get(url)
                self.assertTemplateUsed(response, template)
