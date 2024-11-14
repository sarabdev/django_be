from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, username=None):
        return self.create_user(email=email, password=password, username=username)


# User Model
class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    def __str__(self):
        return self.email

# News Model
class News(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    html = models.TextField()
    media = models.FileField(upload_to="news/")

    def __str__(self):
        return self.title

# Recipe Model
class Recipe(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    category = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=100)
    portions = models.PositiveIntegerField()
    time = models.PositiveIntegerField()
    image = models.ImageField(upload_to="recipes/")
    ingredients = models.JSONField()
    steps = models.JSONField()
    tips = models.CharField(max_length=100)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    is_validate = models.BooleanField(default=True)

    def __str__(self):
        return self.title

# Favorites Model
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')
