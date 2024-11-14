from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .models import User, News, Recipe, Favorite
from .serializers import UserSerializer, NewsSerializer, RecipeSerializer, FavoriteSerializer
import json
from rest_framework_simplejwt.tokens import RefreshToken

# Signup View
class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
            return Response({
                "success": True,
                "message": "User registered successfully.",
                "data": {
                    "user": user_data,
                    "token": str(refresh.access_token)
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "User registration failed. Please check the provided data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({
                "success": False,
                "message": "Both email and password are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({
                "success": False,
                "message": "No account found with this email."
            }, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({
                "success": False,
                "message": "Invalid password. Please try again."
            }, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        return Response({
            "success": True,
            "message": "Login successful.",
            "data": {
                "user": user_data,
                "token": str(refresh.access_token)
            }
        }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_user(request):
    user = request.user
    user.delete()
    return Response({
        "success": True,
        "message": "User account has been removed successfully."
    }, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def news(request):
    if request.method == 'GET':
        news_items = News.objects.all()
        serializer = NewsSerializer(news_items, many=True)
        return Response({
            "success": True,
            "message": "News fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Authentication credentials were not provided."
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "News added successfully."
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "message": "Failed to add news. Please check the provided data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def recipes(request):
    if request.method == 'GET':
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        recipe_id = request.query_params.get('id')

        recipes = Recipe.objects.filter(is_validate=True)
        if recipe_id:
            recipes = recipes.filter(id=recipe_id)
        elif category:
            recipes = recipes.filter(category__iexact=category)
        elif search:
            recipes = recipes.filter(title__icontains=search)

        serializer = RecipeSerializer(recipes, many=True)
        return Response({
            "success": True,
            "message": "Recipes fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({
                "success": False,
                "message": "Authentication credentials were not provided."
            }, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        try:
            ingredients = json.loads(data.get('ingredients', '[]'))
            steps = json.loads(data.get('steps', '[]'))
        except json.JSONDecodeError:
            return Response({
                "success": False,
                "message": "Invalid JSON format for ingredients or steps. Please provide valid JSON."
            }, status=status.HTTP_400_BAD_REQUEST)

        recipe_data = {
            'title': data.get('title'),
            'date': data.get('date'),
            'category': data.get('category'),
            'difficulty': data.get('difficulty'),
            'portions': data.get('portions'),
            'time': data.get('time'),
            'image': request.FILES.get('image'),
            'ingredients': ingredients,
            'steps': steps,
            'tips': data.get('tips'),
            'userId': request.user.id,
            'username': request.user.username,
            'is_validate': data.get('is_validate', True)
        }

        serializer = RecipeSerializer(data=recipe_data)
        if serializer.is_valid():
            serializer.save(userId=request.user, username=request.user.username)
            return Response({
                "success": True,
                "message": "Recipe added successfully."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Failed to add recipe. Please check the provided data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_recipes(request):
    recipes = Recipe.objects.filter(userId_id=request.user)
    serializer = RecipeSerializer(recipes, many=True)

    if recipes.exists():
        return Response({
            "success": True,
            "message": "Your recipes fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            "success": True,
            "message": "No recipes found for this user.",
            "data": []
        }, status=status.HTTP_200_OK)


@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorites(request):
    if request.method == 'POST':
        recipe_id = request.data.get("id")
        if not recipe_id:
            return Response({
                "success": False,
                "message": "Recipe ID is required to add to favorites."
            }, status=status.HTTP_400_BAD_REQUEST)

        recipe = Recipe.objects.filter(id=recipe_id).first()
        if not recipe:
            return Response({
                "success": False,
                "message": "Recipe not found."
            }, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        if not created:
            return Response({
                "success": False,
                "message": "This recipe is already in your favorites."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": True,
            "message": "Recipe added to favorites successfully."
        }, status=status.HTTP_201_CREATED)

    elif request.method == 'GET':
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)

        if favorites.exists():
            return Response({
                "success": True,
                "message": "Favorite recipes fetched successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": True,
                "message": "No favorite recipes found.",
                "data": []
            }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        recipe_id = request.query_params.get("id")
        if not recipe_id:
            return Response({
                "success": False,
                "message": "Recipe ID is required to remove from favorites."
            }, status=status.HTTP_400_BAD_REQUEST)

        favorite = Favorite.objects.filter(user=request.user, recipe_id=recipe_id).first()
        if not favorite:
            return Response({
                "success": False,
                "message": "Favorite not found for the given recipe ID."
            }, status=status.HTTP_404_NOT_FOUND)

        favorite.delete()
        return Response({
            "success": True,
            "message": "Recipe removed from favorites successfully."
        }, status=status.HTTP_200_OK)
