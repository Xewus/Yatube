from django.forms import ModelForm, Textarea
from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {
            'group': 'Выберите сообщество, соответствующую тематике поста',
            'text': 'А здесь обязательно нужно написать Ваш пост!',
            'image': 'Вставьте картинку'}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {'text': 'Вставьте свои пять копеек'}
        widgets = {'text': Textarea(attrs={'cols': '100', 'rows': '1'})}
