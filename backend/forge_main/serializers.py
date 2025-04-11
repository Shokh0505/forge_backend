from rest_framework import serializers
from .models import User, Challenge

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_photo']

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            "id",
            "challenge_title",
            "description",
            "challenge_photo",
            "start_time",
            "finish_time",
        ]

class ChallengeListSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    participants = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Challenge
        fields = '__all__'
    
    
