from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Comment, Follow, Group, Post, User


TEST_DIR = settings.BASE_DIR + '/test_data'


class FormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USER = 'User'
        cls.USER_2 = 'User_2'
        cls.TEXT = 'Test text'
        cls.TEXT_2 = 'Test text 2'
        cls.GROUP = 'Test group'
        cls.GROUP_2 = 'Test group 2'
        cls.DESC = 'Test description'
        cls.DESC_2 = 'Test description 2'
        cls.SLUG = 'test_group'
        cls.SLUG_2 = 'test_group_2'
        cls.user = User.objects.create(username=cls.USER)
        cls.user_2 = User.objects.create(username=cls.USER_2)
        cls.POST = Post.objects.create(text=cls.TEXT,
                                       author=cls.user)

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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(FormTest.user)
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

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
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

    def test_unable_create_comment_by_anonim(self):
        comments = Comment.objects.filter(post=FormTest.POST.id).count()
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                    'username': FormTest.USER, 'post_id': FormTest.POST.id}),
            data={'text': FormTest.TEXT_2},
            follow=True
        )
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{FormTest.USER}/{FormTest.POST.id}/comment',
            HTTPStatus.FOUND)
        self.assertEqual(
            Comment.objects.filter(post=FormTest.POST.id).count(), comments)
        self.assertEqual(Post.objects.count(), self.posts_count)

    def test_create_comment(self):
        comments = Comment.objects.filter(post=FormTest.POST.id).count()
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                    'username': FormTest.USER, 'post_id': FormTest.POST.id}),
            data={'text': FormTest.TEXT_2},
            follow=True
        )
        # Комментарий создался с верными данными
        self.assertTrue(Comment.objects.filter(post=FormTest.POST.id,
                                               author=FormTest.user,
                                               text=FormTest.TEXT_2))
        # перенаправление на страницу поста после комментирования
        self.assertRedirects(
            response,
            f'/{FormTest.USER}/{FormTest.POST.id}/',
            HTTPStatus.FOUND
        )
        # комметариев должно стать на 1 больше
        self.assertEqual(
            Comment.objects.filter(post=FormTest.POST.id).count(), comments + 1
        )
        # На всякий случай проверим, что количество постов не изменилось
        self.assertEqual(Post.objects.count(), self.posts_count)

    def test_follow(self):
        follow_count = Follow.objects.count()
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': FormTest.USER_2}),
            follow=True)
        # количество подписок должно увеличиться на 1
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        # Подписка создалась с верными данными
        self.assertTrue(Follow.objects.filter(user=FormTest.user,
                                              author=FormTest.user_2))
        # На всякий случай проверим, что обратной подписки не создалось
        self.assertFalse(Follow.objects.filter(user=FormTest.user_2,
                                               author=FormTest.user))

    def test_unfollow(self):
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': FormTest.USER_2}),
            follow=True)
        follow_count = Follow.objects.count()
        self.authorized_client.post(reverse(
            'posts:profile_unfollow', kwargs={'username': FormTest.USER_2}),
            follow=True)
        # количество подписок должно уменьшиться на 1
        self.assertEqual(Follow.objects.count(), follow_count - 1)
        # Подписка с переданными данными не должна существовать
        self.assertFalse(Follow.objects.filter(user=FormTest.user,
                                               author=FormTest.user_2))

    def test_unable_selffollow(self):
        follow_count = Follow.objects.count()
        self.authorized_client.post(reverse(
            'posts:profile_follow', kwargs={'username': FormTest.USER}),
            follow=True)
        # количество подписок должно измениться
        self.assertEqual(Follow.objects.count(), follow_count)
        # Подписка с переданными данными не должна существовать
        self.assertFalse(Follow.objects.filter(user=FormTest.user,
                                               author=FormTest.user))
