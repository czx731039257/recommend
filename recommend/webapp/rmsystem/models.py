from django.db import models

# Create your models here.
class Movie(models.Model):
    id=models.IntegerField(primary_key=True)
    title=models.CharField(max_length=255)
    genres=models.CharField(max_length=255)
    feature=models.CharField(max_length=255)
    number_people=models.IntegerField()

class User(models.Model):
    id=models.IntegerField(primary_key=True)
    username=models.CharField(max_length=255)
    password=models.CharField(max_length=20)
    A1=models.CharField(max_length=255)
    A2 = models.CharField(max_length=255)
    A3 = models.CharField(max_length=255)
    A4 = models.CharField(max_length=255)
    A5 = models.CharField(max_length=255)
    A6 = models.CharField(max_length=255)
    A7 = models.CharField(max_length=255)
    A8 = models.CharField(max_length=255)
    A9 = models.CharField(max_length=255)
    A10 = models.CharField(max_length=255)
    b=models.CharField(max_length=255)
    theta=models.CharField(max_length=255)
    Cluster=models.ForeignKey('Cluster',on_delete=models.CASCADE)
    sex=models.CharField(max_length=255)
    phone=models.CharField(max_length=255)
    email=models.CharField(max_length=255)
    head=models.CharField(max_length=255)
    remarks=models.CharField(max_length=255)
    Role = models.ForeignKey('Role', on_delete=models.CASCADE)

class Genres(models.Model):
    id=models.IntegerField(primary_key=True)
    name_en=models.CharField(max_length=255)
    name_ch=models.CharField(max_length=255)

class Movie_Genres(models.Model):
    Movie=models.ForeignKey('Movie',on_delete=models.CASCADE)
    Genres = models.ForeignKey('Genres', on_delete=models.CASCADE)

class Cluster(models.Model):
    id=models.IntegerField(primary_key=True)
    A1 = models.CharField(max_length=255)
    A2 = models.CharField(max_length=255)
    A3 = models.CharField(max_length=255)
    A4 = models.CharField(max_length=255)
    A5 = models.CharField(max_length=255)
    A6 = models.CharField(max_length=255)
    A7 = models.CharField(max_length=255)
    A8 = models.CharField(max_length=255)
    A9 = models.CharField(max_length=255)
    A10 = models.CharField(max_length=255)
    b = models.CharField(max_length=255)
    theta = models.CharField(max_length=255)

class Collect(models.Model):
    User = models.ForeignKey('User', on_delete=models.CASCADE)
    Movie = models.ForeignKey('Movie', on_delete=models.CASCADE)

class Record(models.Model):
    User=models.ForeignKey('User',on_delete=models.CASCADE)
    Movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    time=models.DateTimeField(auto_now=True)
    click=models.IntegerField()

class Permission(models.Model):
    name=models.CharField(max_length=255)
    url=models.CharField(max_length=255)
    describe=models.CharField(max_length=255)

class Role(models.Model):
    name = models.CharField(max_length=255)
    describe = models.CharField(max_length=255)


class Role_Permission(models.Model):
    Role = models.ForeignKey('Role', on_delete=models.CASCADE)
    Permission = models.ForeignKey('Permission', on_delete=models.CASCADE)

