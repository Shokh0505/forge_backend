from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from .serializers import SignupSerializer, UserSerializer, ChallengeSerializer, ChallengeListSerializer, MessageSerializer, UserSerializerID
from django.http import JsonResponse
from .models import User, Challenge, ChallengeLike, ChallengeRecord, Chat, Message, Settings, WhitelistPeople
from datetime import date, datetime, timedelta
from collections import defaultdict

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
    user = request.user
    challenges = Challenge.objects.all().order_by('-created_at')
    paginator = Paginator(challenges, 10)
    likedChallengeIDs  = []

    page_number = request.GET.get('page') or 1
    page_objects = paginator.get_page(page_number)

    for object in page_objects:
        if ChallengeLike.objects.filter(user=user, challenge=object):
            likedChallengeIDs.append(str(object.id))

    serializer = ChallengeListSerializer(page_objects, many=True)

    next_page = page_objects.next_page_number() if page_objects.has_next() else None
    prev_page = page_objects.previous_page_number() if page_objects.has_previous() else None

    base_url = request.build_absolute_uri('?')
    base_url = base_url.split('?')[0]


    return Response({
        "message": "success",
        "results": serializer.data,
        "next": next_page if next_page else None,
        "previous": prev_page if prev_page else None,
        "count": paginator.count,
        "likedIDs": likedChallengeIDs
    }, status=status.HTTP_200_OK)

class LikeChallenge(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        challengeID = request.data.get('id')

        challenge = Challenge.objects.get(id=challengeID)
        if challenge is None:
            return Response({"message": "coudn't find a valid id for the challenge"}, status=status.HTTP_400_BAD_REQUEST)
        
        if ChallengeLike.objects.filter(user=user, challenge=challenge).exists():
            return Response({"message": "You already have like the challenge"}, status=status.HTTP_400_BAD_REQUEST)

        ChallengeLike.objects.create(user=user, challenge=challenge)
        return Response({"messsage": "success"}, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        user = request.user
        challengeID = request.data.get('id')
        challenge = Challenge.objects.get(id=challengeID)
        
        if challenge is None:
            return Response({"message": "coudn't find a valid id for the challenge"}, status=status.HTTP_400_BAD_REQUEST)
        
        like = ChallengeLike.objects.filter(user=user, challenge=challenge).first()
        
        if like:
            like.delete()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response({"message": "You didn't like the challenge in the first place"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def joinChallenge(request):
    user = request.user
    challengeID = request.data.get('challengeID')

    challenge = Challenge.objects.get(id=challengeID)

    if challenge is None:
        return Response({"message": "error", "description": "provided email is not valid"}, status=status.HTTP_400_BAD_REQUEST)
    

    finish_time = challenge.finish_time
    if finish_time is None:
        return Response({"message": "error", "description": "Correct timeline was not given for the challange"}, status=status.HTTP_400_BAD_REQUEST)

    current_date = date.today()

    if current_date >= finish_time:
        return Response({"message": "error", "description": "The challenge time has already passed"}, status=status.HTTP_400_BAD_REQUEST)

    challenge.participants.add(user)

    return Response({"message": "success"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def leaveChallenge(request):
    user = request.user
    challengeID = request.data.get('challengeID')

    challenge = Challenge.objects.get(id=challengeID)

    if challenge is None:
        return Response({"message": "error", "description": "Provided id is not valid"}, status=400)

    challenge.participants.remove(user)

    return Response({"message": "success"}, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def finishedChallengeToday(request):
    user = request.user
    challengeID = request.data.get('challengeID')

    challenge = Challenge.objects.get(id=challengeID)

    if challenge is None:
        return Response({"message": "error", "description": "Provided id is not valid"}, status=400)

    current_time = date.today()

    if ChallengeRecord.objects.filter(user=user, challenge=challenge, date=current_time).exists():
        return Response({"message": "error", "description": "you have already provided data"}, status=400)
    
    ChallengeRecord.objects.create(user=user, challenge=challenge, date=current_time)

    return Response({"message": "success"}, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def groupChallengeStats(request):
    user = request.user
    challengeID = request.data.get('challengeID')
    data = {}

    challenge = Challenge.objects.get(id=challengeID)
    if challenge is None:
        return Response({"message": "error", "description": "provided id is not valid"}, status=400)

    data["isJoined"] = challenge.isParticipant(user)

    serializerOwner = UserSerializerID(challenge.owner)
    data["owner"] = serializerOwner.data
    data["challengeTitle"] = challenge.challenge_title
    
    # the user has done the challenge today?
    current_time = date.today()
    data["isFinishedToday"] = ChallengeRecord.objects.filter(user=user, challenge=challenge, date=current_time).exists()

    data["daysPassed"] = (current_time - challenge.start_time).days
    data["todayGroupCompletePercent"] = challenge.overallPercentageToday()
    data["streakGroup"] = challenge.streakGroup()
    
    topUserIDs = challenge.topPeople()
    user_ids = [entry['user'] for entry in topUserIDs]
    users = User.objects.filter(id__in=user_ids)
    serialized_users = UserSerializer(users, many=True)

    data["topLeaders"] = serialized_users.data

    return Response({"message": "success", "data": data}, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getChallengeStreak(request):
    challengeID = request.data.get('challengeID')
    date_data = request.data.get("date")

    challenge = Challenge.objects.get(id=challengeID)
    if challenge is None:
        return Response({"message": "error", "description": "not valid id was provided"}, status=status.HTTP_400_BAD_REQUEST)
    if date_data is None:
        return Response({"message": "error", "description": "date is not provided"}, status=status.HTTP_400_BAD_REQUEST)

    data_format = "%Y-%m-%d"
    data_obj = datetime.strptime(date_data, data_format).date()

    start_date = date(data_obj.year, data_obj.month, 1)
    end_date = date(data_obj.year, data_obj.month + 1, 1) - timedelta(days=1)

    records = ChallengeRecord.objects.filter(
        challenge=challenge,
        date__range=[start_date, end_date]
    ).values('user', 'date')

    date_to_users = defaultdict(set)

    for record in records:
        date_to_users[record['date']].add(record['user'])

    data = []
    total = challenge.participants.count()

    for day in date_to_users:
        done = len(date_to_users[day])
        percentage = int((done / total) * 100) if total else 0
        data.append({'date': day, 'percentage': percentage})

    return Response({"message": "success", "data": data}, status=200)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getParticipatedChallenges(request):
    user = request.user
    challengesToSend = []

    challenges = user.challenges.all()

    for challenge in challenges:
        data = dict()
        data['id'] = challenge.id
        data['days'] = (date.today() - challenge.start_time).days
        data['percentage'] = challenge.overallPercentageToday()
        data['streak'] = challenge.streakUser(user)
        owner = UserSerializer(challenge.owner).data
        data['owner'] = owner
        data['challengeTitle'] = challenge.challenge_title
        challengesToSend.append(data)

    return Response({"message": "success", "data": challengesToSend}, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getMessages(request):
    user = request.user
    chat_partner = request.data.get("partnerID")
    chat_partner = User.objects.get(id=chat_partner)
    chat = None


    if chat_partner is None:
        return Response({"message": "Not valid id was given"}, status=400)

    if int(user.id) > int(chat_partner.id):
        chat = Chat.objects.filter(user1=chat_partner, user2=user).first()
    else:
        chat = Chat.objects.filter(user1=user, user2=chat_partner).first()


    if chat is None:
        return Response({
                            "message": "No chat has been created", 
                            "data": None,
                            "next": None
                        })
    
    messages = Message.objects.filter(chat=chat).order_by('-sent_at')
    paginator = Paginator(messages, 10)
    page_number = request.GET.get('page')


    if page_number is None or not page_number.isnumeric():
        return Response({"message": "Query was given incorrectly"}, status=400)

    if not page_number.isnumeric() or int(page_number) > paginator.num_pages:
        return Response({"message": "sucess", "data": None, "next": False})

    page = paginator.page(page_number)
    serializer = MessageSerializer(page, many=True)

    return Response({"message": "success", "data": serializer.data, 'next': page.has_next()})

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_inbox_people(request):
    user = request.user
    inbox_people = user.get_all_chats()

    final_data = []

    for person in inbox_people:
        serialized_data = {}
        
        user_serialized = UserSerializerID(person['user'])
        serialized_data['user'] = user_serialized.data

        message_serialized = MessageSerializer(person['last_message'])
        serialized_data['last_message'] = message_serialized.data
        final_data.append(serialized_data)

    return Response({"message": "success", "data": final_data}, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_profile_photo(request):
    user = request.user
    picture = request.data.get('picture')

    if not picture:
        return Response({"message": "Picuture is not valid"}, status=400)
    
    user.profile_photo = picture    
    user.save()

    return Response({"message": "Success"}, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def changeBIO(request):
    user = request.user
    bio = request.data.get('bio')

    if not bio or len(bio) > 500:
        return Response({"message": "error", "description": "invalid bio"}, status=400)

    user.bio = bio
    user.save()

    return Response({"message": "success"}, status=200)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def toggle_allow_messaging(request):
    user = request.user
    
    if Settings.objects.filter(user=user).exists():
        user.user_settings.allow_messaging = not user.user_settings.allow_messaging
        user.user_settings.save()
    else:
        settings = Settings.objects.create(user=user, allow_messaging=False)
        settings.save()
    
    return Response({"message": "success"}, status=200)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_white_list(request):
    user = request.user
    allowed_person_username = request.data.get('username')

    allowed_person = User.objects.get(username=allowed_person_username)
    if user is None:
        return Response({"message": "success", "description": "This username doesn't exist"}, status=400)
    
    WhitelistPeople.objects.create(user=user, allowed_person=allowed_person)
    
    settings = Settings.objects.get(user=user)
    if settings is None:
        settings = Settings.objects.create(user=user, allow_messaging=False)

    settings.has_whitelist = True
    settings.save()

    return Response({"message": "success"}, status=200)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_whiteListed_people(request):
    user = request.user

    whitelist_people = user.whitelist_people.all()

    serialized_data = []

    for person in whitelist_people:
        serialized_whitelist = UserSerializerID(person.allowed_person)
        serialized_data.append(serialized_whitelist.data)

    return Response({"message": "success", "data": serialized_data}, status=200)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def is_messaging_allowed(request):
    user = request.user
    isAllowed = user.user_settings.allow_messaging
    return Response({"message": "success", "isAllowed": isAllowed}, status=200)