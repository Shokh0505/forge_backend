from django.urls import path
from .views import homeIndex, signup, whoAmI, login, createChallenge, getChallenges, LikeChallenge, joinChallenge, leaveChallenge, finishedChallengeToday, groupChallengeStats, getChallengeStreak
from .views import getParticipatedChallenges, getMessages, get_inbox_people, update_profile_photo, changeBIO
from .views import *
from rest_framework.authtoken import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', homeIndex, name='home'),
    # Authentication stuff
    path('signup/', signup, name='signup'),
    path('login/', login, name="login"),
    path('api-token-auth/', auth_views.obtain_auth_token, name='obtainToken'),
    path('whoAmI/', whoAmI, name='who_am_I'),
    # Managing the challenges
    path('createChallenge/', createChallenge, name="create_challenge"),
    path('getChallenges/', getChallenges, name='get_challenges'),
    path('likeChallenge/', LikeChallenge.as_view(), name='like_challenge'),
    path('joinChallenge/', joinChallenge, name='join_challenge'),
    path('leaveChallenge/', leaveChallenge, name='leaveChallenge'),
    path('finishChallengeToday/', finishedChallengeToday),
    path('groupChallangeStats/', groupChallengeStats),
    path('getChallengeStreak/', getChallengeStreak),
    path('getParticipatedChallenge/', getParticipatedChallenges),
    # Inbox
    path('getMessages/', getMessages, name='getMessages'),
    path('getInboxPeople/', get_inbox_people, name='get_inbox_people'),
    path('get_username/', get_username, name='get_username'),
    # Settings
    path('update_profile_picture/', update_profile_photo),
    path('changeBIO/', changeBIO, name='changeBIO'),
    path('toggle_allow_messaging/', toggle_allow_messaging, name='toggle_allow_messaging'),
    path('add_white_list/', add_white_list, name='add_white_list'),
    path('get_whiteListed_people/', get_whiteListed_people, name='get_whiteListed_people'),
    path('is_messaging_allowed/', is_messaging_allowed, name='is_messaging_allowed'),# for the user himself
    path('remove_white_list/', remove_whitelist, name='remove_white_list'),
    path('allowed_messaging/', allowedMessaging, name='allowedMessaging'), # for other users 

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)