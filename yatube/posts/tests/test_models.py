import datetime as dt
from django.test import TestCase
from ..forms import CommentForm, PostForm
from ..models import Comment, Follow, Group, Post, User


class ModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Test group',
            description='Description of Test group',
            slug='group'
        )
        cls.user = User.objects.create(
            username='Qwerty'
        )
        cls.user_2 = User.objects.create(
            username='qaz'
        )
        cls.post = Post.objects.create(
            text='Test text' * 3,
            pub_date=dt.datetime.now(),
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            text='Какой-то комментарий',
            author=cls.user_2,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.user_2,
            author=cls.user,
        )
        cls.model_str = {
            cls.comment: cls.comment.text[:15],
            cls.follow: 'qaz-->Qwerty',
            cls.group: cls.group.title,
            cls.post: cls.post.text[:15],
        }
        cls.form_post = PostForm()
        cls.form_comment = CommentForm()

    def test_str_models(self):
        for model, value in ModelTests.model_str.items():
            with self.subTest(model=model):
                act = str(model)
                self.assertEqual(act, value)

    def test_labels_post(self):
        labels = {'group': 'Сообщество',
                  'text': 'Текст поста'}
        for label, value in labels.items():
            with self.subTest(label=label):
                label = ModelTests.form_post.fields[label].label
                self.assertEqual(label, value)

    def test_help_texts_post(self):
        help_texts = {
            'group': 'Выберите сообщество, соответствующую тематике поста',
            'text': 'А здесь обязательно нужно написать Ваш пост!'}
        for text, value in help_texts.items():
            with self.subTest(text=text):
                text = ModelTests.form_post.fields[text].help_text
                self.assertEqual(text, value)

    def test_labels_comment(self):
        labels = {'text': 'Текст комментария'}
        for label, value in labels.items():
            with self.subTest(label=label):
                label = ModelTests.form_comment.fields[label].label
                self.assertEqual(label, value)

    def test_help_texts_comment(self):
        help_texts = {'text': 'Вставьте свои пять копеек'}
        for text, value in help_texts.items():
            with self.subTest(text=text):
                text = ModelTests.form_comment.fields[text].help_text
                self.assertEqual(text, value)
