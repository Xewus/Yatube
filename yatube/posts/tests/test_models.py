import datetime as dt
from django.test import TestCase
from posts.forms import PostForm
from posts.models import Group, Post, User


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
        cls.post = Post.objects.create(
            text='Test text' * 3,
            pub_date=dt.datetime.now(),
            author=cls.user
        )
        cls.model_str = {
            cls.group: cls.group.title,
            cls.post: cls.post.text[:15],
        }
        cls.form = PostForm()

    def test_str_models(self):
        for model, value in ModelTests.model_str.items():
            with self.subTest(model=model):
                act = str(model)
                self.assertEqual(act, value)

    def test_labels(self):
        labels = {'group': 'Сообщество', 'text': 'Текст поста'}
        for label, value in labels.items():
            with self.subTest(label=label):
                label = ModelTests.form.fields[label].label
                self.assertEqual(label, value)

    def test_help_texts(self):
        help_texts = {
            'group': 'Выберите сообщество, соответствующую тематике поста',
            'text': 'А здесь обязательно нужно написать Ваш пост!'}
        for text, value in help_texts.items():
            with self.subTest(text=text):
                text = ModelTests.form.fields[text].help_text
                self.assertEqual(text, value)
