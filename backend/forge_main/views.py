from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from .serializers import SignupSerializer, UserSerializer, ChallengeSerializer, ChallengeListSerializer
from django.http import JsonResponse
from .models import User, Challenge

def homeIndex(request):
    return render(request, 'home.html')

@api_view(['POST'])
def signup(request):

    # check if username already exists
    if User.objects.filter(username=request.data.get('username')).exists():
        return Response({"error": "The username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "user created successfully"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        response = JsonResponse({"messege": "Login successful"})
        response.set_cookie(
            key="auth_token",
            value=token.key,
            httponly=True,  
            # uncomment this in production
            #secure=True,  
            samesite="Lax"
        )

        return response
    else:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def whoAmI(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response({"message": "success", "user": serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createChallenge(request):
    serializer = ChallengeSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response({"message": "success"}, status=status.HTTP_201_CREATED)
    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getChallenges(request):
    challenges = Challenge.objects.all().order_by('-created_at')
    paginator = Paginator(challenges, 10)

    page_number = request.GET.get('page')
    page_objects = paginator.get_page(page_number)

    serializer = ChallengeListSerializer(page_objects, many=True)

    return Response({"message": "success", "results": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def simple(request):
    return Response({"message": "The endpoint is working"}, status=status.HTTP_401_UNAUTHORIZED)



