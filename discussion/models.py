from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
import datetime

class Board(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=100,blank=False, null=False)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE,related_name='topics')
    author =  models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    views = models.PositiveIntegerField(default=0)  # <- here

    def __str__(self):
        return "{}'s {}".format(str(self.author), self.subject)

    class Meta:
        verbose_name_plural = "Topic"


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic,on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(get_user_model(),
        on_delete=models.CASCADE, related_name='posts')
    updated_by = models.ForeignKey(get_user_model(),
        on_delete=models.CASCADE, null=True, related_name='+')

    def __str__(self):
        return 'posted by {}'.format(str(self.created_by))

    class Meta:
        verbose_name_plural = "Post"



