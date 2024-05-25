from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from .resources import POST_TYPE_CHOICES
from django.db.models.functions import Coalesce
from django.db.models import Sum


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Author(models.Model):
    author_name = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.IntegerField(default=0)

    def generate(self):
        post_rating = Post.objects.filter(post_author=self.pk).aggregate(post_rating_sum=Coalesce(
            Sum('post_rating') * 3, 0))
        comment_rating = Comment.objects.filter(comment_author=self.author_name).aggregate(comment_rating_sum=Coalesce(
            Sum('comment_rating'), 0))
        post_comment_rating = Comment.objects.filter(comment_post__post_author__author_name=self.author_name).aggregate(
            comment_rating_sum=Coalesce(
                Sum('comment_rating'), 0))
        self.author_rating = (post_rating['post_rating_sum'] + comment_rating['comment_rating_sum']
                              + post_comment_rating['comment_rating_sum'])

        self.save()

    def __str__(self):
        return self.author_name.username


class Category(models.Model):
    category_name = models.CharField(max_length=64, unique=True, verbose_name="Category")

    # subscribers = models.ManyToManyField(User, blank=True, null=True, related_name='categories')

    def __str__(self):
        return self.category_name


class Post(models.Model):
    post_author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    post_type = models.CharField(max_length=1, choices=POST_TYPE_CHOICES, verbose_name='Тип поста')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    categories = models.ManyToManyField(Category, through='PostCategory', verbose_name="Категория")
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    content = models.TextField(blank=True, verbose_name="Содержание")
    post_rating = models.IntegerField(default=0)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        return f'{self.content[:123]}...'

    def get_absolute_url(self):
        return reverse('post_id', args=[str(self.id)])

    def __str__(self):
        return self.title


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()


class Subscription(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    category = models.ForeignKey(
        to='Category',
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
