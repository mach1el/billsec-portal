from django.db import models

class ProjectInfo(models.Model):
  host = models.CharField(max_length=255)
  port = models.IntegerField()
  schema_name = models.CharField(max_length=255)
  user = models.CharField(max_length=255)
  password = models.CharField(max_length=255)

  def __str__(self):
    return f"{self.host}:{self.port}"