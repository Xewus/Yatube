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
    text = models.TextField("Текст поста")
    pub_date = models.DateTimeField("Дата публикации",
                                    auto_now_add=True)
    author = models.ForeignKey(User, models.CASCADE,
                               related_name="posts",
                               verbose_name="Автор")
    image = models.ImageField(upload_to='posts/',
                              verbose_name='Картинка',
                              blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT,
                              related_name='posts',
                              verbose_name='Сообщество',
                              blank=True, null=True)

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.text[:15]
