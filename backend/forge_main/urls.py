from django.urls import path
from .views import homeIndex, signup, whoAmI, login, createChallenge, getChallenges
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
    path('createChallenge/', createChallenge, name="create_challenge"),
    path('getChallenges/', getChallenges, name='get_challenges'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)