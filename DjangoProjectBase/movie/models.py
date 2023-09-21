from django.db import models
from django.contrib.auth.models import User
from openai.embeddings_utils import get_embedding, cosine_similarity
import numpy as np


def get_default_array():
  default_arr = np.random.rand(1536)  # Adjust this to your desired default array
  return default_arr.tobytes()

class Movie(models.Model):
  title = models.CharField(max_length=100)
  description = models.CharField(max_length=1000)
  image = models.ImageField(upload_to='movie/images/', default = 'movie/images/default.jpg')
  url = models.URLField(blank=True)
  emb = models.BinaryField(default=get_default_array())
  
  def __str__(self):
    return self.title

class Review(models.Model):
  text = models.CharField(max_length=100)
  date = models.DateTimeField(auto_now_add=True)
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
  watchAgain = models.BooleanField()
 
  def __str__(self):
    return self.text
