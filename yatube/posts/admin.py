from django.contrib import admin
from .models import Comment, Post, Group


class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('id', 'text', 'pub_date', 'author', 'group')
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('pub_date', 'group')
    list_editable = ('group', 'text',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'slug',)
    search_fields = ('title',)
    list_filter = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'created', 'author', 'post')
    search_fields = ('text', 'author', 'post')
    list_filter = ('created', 'author', 'post')
    list_editable = ('text',)


admin.site.register(Comment, CommentAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
