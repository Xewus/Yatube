from django import forms
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from yatube.settings import POSTS_ON_PAGE
from ..models import Group, Post, User


class ViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = 'User'
        cls.USER_2 = 'Method_User'
        cls.TEXT = 'Test text'
        cls.TEXT_2 = 'Test text_2'
        cls.GROUP = 'Test group'
        cls.GROUP_2 = 'Test group 2'
        cls.DESC = 'Test description'
        cls.DESC_2 = 'Test description 2'
        cls.SLUG = 'test_group'
        cls.SLUG_2 = 'test_group_2'
        cls.urls_templates_guest = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group', kwargs={
                'slug': cls.SLUG}): 'posts/group.html',
            reverse('posts:profile', kwargs={
                'username': cls.USER}): 'posts/profile.html',
            reverse('posts:post', kwargs={
                'username': cls.USER, 'post_id': 1}): 'posts/post.html',
        }
        cls.urls_templates_user = {
            reverse('posts:new_post'): 'posts/new.html'
        }
        cls.url_with_paginator = (
            reverse('posts:index'),
            reverse('posts:group', kwargs={'slug': cls.SLUG}),
            reverse('posts:profile', kwargs={'username': cls.USER}),
        )
        cls.urls_templates = {
            **cls.urls_templates_guest, **cls.urls_templates_user
        }
        cls.group_1 = Group.objects.create(
            title=cls.GROUP,
            description=cls.DESC,
            slug=cls.SLUG
        )
        cls.group_2 = Group.objects.create(
            title=cls.GROUP_2,
            description=cls.DESC_2,
            slug=cls.SLUG_2)

        cls.user = User.objects.create(username=cls.USER)

        Post.objects.bulk_create([
            Post(
                text=cls.TEXT_2, author=cls.user, group=cls.group_1
            ) for i in range(POSTS_ON_PAGE + 1)
        ])

    def setUp(self):
        self.client_1 = Client()
        self.client_1.force_login(ViewsTest.user)
        cache.clear()

    def test_using_templates_of_pages(self):
        urls_templates = {**ViewsTest.urls_templates,
                          **{'zzzzzz/': 'misc/404.html'}}
        for url, template in urls_templates.items():
            with self.subTest(template=template):
                response = self.client_1.get(url)
                self.assertTemplateUsed(response, template)

    def test_using_templates_for_post_edit(self):
        user = User.objects.create(username=ViewsTest.USER_2)
        client_2 = Client()
        client_2.force_login(user)
        url_edit = reverse('posts:post_edit', kwargs={
            'username': ViewsTest.USER, "post_id": POSTS_ON_PAGE + 1})

        response = self.client_1.get(url_edit)
        self.assertTemplateUsed(response, 'posts/new.html')
        response = client_2.get(url_edit)
        self.assertTemplateNotUsed(response, 'posts/new.html')

    def test_context_form_for_page_new_post(self):
        response = self.client_1.get(reverse('posts:new_post'))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField,
                       'image': forms.fields.ImageField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context['form'].fields[value]
                self.assertIsInstance(field, expected)

    def test_paginator(self):
        for url in ViewsTest.url_with_paginator:
            with self.subTest(url=url):
                response = self.client_1.get(url)
                self.assertEqual(len(response.context['page']),
                                 POSTS_ON_PAGE)

    def test_out_last_posts_on_page(self):
        for url in ViewsTest.url_with_paginator:
            with self.subTest(url=url):
                response = self.client_1.get(url)
                first_object = response.context['page'][0]
                self.assertEqual(first_object, Post.objects.first())

    def test_new_post_in_correct_group(self):
        posts_group_1 = Post.objects.filter(group=ViewsTest.group_1.id).count()
        posts_group_2 = Post.objects.filter(group=ViewsTest.group_2.id).count()
        self.assertEqual(posts_group_1, POSTS_ON_PAGE + 1)
        self.assertEqual(posts_group_2, 0)

    def test_cache(self):
        posts_count = Post.objects.count()
        response = self.client_1.get(reverse('posts:index')).content
        Post.objects.create(
            text=ViewsTest.TEXT, author=ViewsTest.user, group=ViewsTest.group_2
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            response, self.client_1.get(reverse('posts:index')).content)
        cache.clear()
        self.assertNotEqual(
            response, self.client_1.get(reverse('posts:index')).content)
