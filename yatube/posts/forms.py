from django.forms import ModelForm
from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {
            'group': 'Выберите сообщество, соответствующую тематике поста',
            'text': 'А здесь обязательно нужно написать Ваш пост!',
            'image': 'Вставьте картинку'}
