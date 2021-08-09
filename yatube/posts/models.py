from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Сообщество', max_length=200)
    description = models.TextField('Описание сообщества')
    slug = models.SlugField('URL', unique=True)

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста')
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(User, models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    image = models.ImageField(upload_to='posts/',
                              verbose_name='Картинка',
                              blank=True, null=True)
    group = models.ForeignKey(Group, models.PROTECT,
                              related_name='posts',
                              verbose_name='Сообщество',
                              blank=True, null=True)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(User, models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')
    post = models.ForeignKey(Post, models.CASCADE,
                             related_name='comments',
                             verbose_name='Пост')
    created = models.DateTimeField('Дата публикации',
                                   auto_now_add=True)

    class Meta:
        verbose_name = 'Комметарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, models.CASCADE,
                             related_name="follower",
                             verbose_name='Подписчик')
    author = models.ForeignKey(User, models.CASCADE,
                               related_name="following",
                               verbose_name='Автор')

    class Meta:
        models.UniqueConstraint = (
            ['user', 'author'], '%(app_label)s_%(class)s_is_adult')

    def __str__(self) -> str:
        return f'{self.user.username} --> {self.author.username}'
