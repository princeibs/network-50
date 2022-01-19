from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Comment(models.Model):
    name = models.ForeignKey(User, on_delete=models.PROTECT)
    comment = models.TextField()
    timestamp =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.comment}\n"


class Post(models.Model):
    name = models.ForeignKey(User, on_delete=models.PROTECT)
    post = models.TextField()
    likes = models.ManyToManyField(User, default=0, related_name='post_liked')
    comments = models.ManyToManyField(Comment, blank=True, related_name='comments_post')
    timestamp =  models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.post}\n"


class Follow(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name="followers_all")
    follows = models.ManyToManyField(User, related_name="follows_all")

    def __str__(self):
        return f"\nName: {self.name} \nFollowers - {self.followers.count()}, \nFollows - {self.follows.count()}"
