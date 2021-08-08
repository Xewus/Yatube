import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User


class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.USER = 'User'
        cls.TEXT = 'Test text'
        cls.TEXT_2 = 'Test text 2'
        cls.GROUP = 'Test group'
        cls.GROUP_2 = 'Test group 2'
        cls.DESC = 'Test description'
        cls.DESC_2 = 'Test description 2'
        cls.SLUG = 'test_group'
        cls.SLUG_2 = 'test_group_2'

        cls.group_1 = Group.objects.create(
            title=cls.GROUP,
            description=cls.DESC,
            slug=cls.SLUG
        )
        cls.group_2 = Group.objects.create(
            title=cls.GROUP_2,
            description=cls.DESC_2,
            slug=cls.SLUG_2
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username=FormTest.USER)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.posts_count = Post.objects.count()

    def test_unable_create_post_by_anonim(self):
        response = self.guest_client.post(
            reverse('posts:new_post'),
            data={'text': FormTest.TEXT},
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/new/', HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), self.posts_count)

    def test_create_post_without_group(self):
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data={'text': FormTest.TEXT},
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertRedirects(
            response, reverse('posts:index'), HTTPStatus.FOUND)
        self.assertTrue(Post.objects.filter(text=FormTest.TEXT))
        self.assertFalse(Post.objects.filter(
            text=FormTest.TEXT, group__in=[FormTest.group_1, FormTest.group_2])
        )

    def test_create_post_with_group(self):
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data={'group': FormTest.group_1.id,
                  'text': FormTest.TEXT},
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertRedirects(
            response, reverse('posts:index'), HTTPStatus.FOUND)
        self.assertTrue(Post.objects.filter(
            text=FormTest.TEXT, group=FormTest.group_1))
        self.assertFalse(Post.objects.filter(
            text=FormTest.TEXT, group=FormTest.group_2))

    def test_create_post_with_picture(self):
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(name='small_1.gif',
                                      content=small_gif,
                                      content_type='image/gif')

        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data={'group': FormTest.group_1.id,
                  'text': FormTest.TEXT,
                  'image': uploaded},
            follow=True
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertRedirects(
            response, reverse('posts:index'), HTTPStatus.FOUND)
        self.assertTrue(Post.objects.filter(text=FormTest.TEXT,
                                            author=self.user,
                                            group=FormTest.group_1,
                                            image='posts/small_1.gif'))
        self.assertFalse(Post.objects.filter(
            text=FormTest.TEXT, group=FormTest.group_2))

    def test_edit_post(self):
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(name='small_2.gif',
                                      content=small_gif,
                                      content_type='image/gif')
        Post.objects.create(
            text=FormTest.TEXT, author=self.user, group=FormTest.group_1
        )
        posts_count = Post.objects.count()

        posts_count_group_1 = Post.objects.filter(
            group=FormTest.group_1).count()
        posts_count_group_2 = Post.objects.filter(
            group=FormTest.group_2).count()
        exist_post = Post.objects.get(
            text=FormTest.TEXT, author=self.user, group=FormTest.group_1
        )
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'username': FormTest.USER,
                                               'post_id': exist_post.id}),
            data={'group': FormTest.group_2.id,
                  'text': FormTest.TEXT_2,
                  'image': uploaded},
            follow=True
        )

        self.assertEqual(posts_count, Post.objects.count())
        self.assertRedirects(
            response, reverse('posts:post', kwargs={
                'username': FormTest.USER, 'post_id': exist_post.id}),
            HTTPStatus.FOUND)
        self.assertTrue(Post.objects.filter(text=FormTest.TEXT_2,
                                            author=self.user,
                                            group=FormTest.group_2,
                                            image='posts/small_2.gif'))
        self.assertEqual(posts_count_group_1 - 1, Post.objects.filter(
            group=FormTest.group_1).count())
        self.assertEqual(posts_count_group_2 + 1, Post.objects.filter(
            group=FormTest.group_2).count())

    def test_unable_edit_post_by_not_author(self):
        user = User.objects.create(username='Qwerty')
        user_client = Client()
        user_client.force_login(user)
        post = Post.objects.create(
            text=FormTest.TEXT, author=self.user, group=FormTest.group_1
        )
        posts_count = Post.objects.count()

        for client in self.guest_client, user_client:
            with self.subTest(client=client):
                client.post(
                    reverse('posts:post_edit', kwargs={
                        'username': FormTest.USER, 'post_id': post.id}),
                    data={'group': FormTest.group_2.id,
                          'text': FormTest.TEXT_2},
                    follow=True
                )
                self.assertEqual(Post.objects.count(), posts_count)
                self.assertTrue(Post.objects.filter(text=FormTest.TEXT,
                                                    author=self.user,
                                                    group=FormTest.group_1))
