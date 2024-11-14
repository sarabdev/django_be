from django.urls import path
from .views import SignupView, LoginView, remove_user, news, recipes, my_recipes, favorites

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('remove_user', remove_user, name='remove_user'),
    path('news', news, name='news'),
    path('recipes', recipes, name='recipes'),
    path('recipes/my', my_recipes, name='my_recipes'),
    path('favorites', favorites, name='favorites'),
]
