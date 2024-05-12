from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Follow(models.Model):
    follower = models.ForeignKey(User,on_delete=models.CASCADE,related_name="following")
    followed = models.ForeignKey(User,on_delete=models.CASCADE,related_name="followers")

class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="posts")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    
    
class Like(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="post_likes")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="likes")
    timestamp = models.DateTimeField(auto_now_add=True)
