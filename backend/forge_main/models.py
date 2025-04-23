from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError 
from datetime import date, timedelta
from django.db.models import Count

class User(AbstractUser):
    profile_photo = models.TextField(max_length=15, default="default1.png")
    
class Challenge(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    challenge_photo = models.ImageField(upload_to='challenges/', null=True, blank=True)
    challenge_title = models.TextField(max_length=500, default="No title")
    description = models.TextField(max_length=500)
    start_time = models.DateField(blank=True, null=True)
    finish_time = models.DateField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name="challenges")

    def __str__(self):
        return f"Challenge: {self.challenge_title}"

    @property
    def likes(self):
        return self.likes.count()

    def isParticipant(self, user):
        return self.participants.filter(id=user.id).exists()
    
    def overallPercentageToday(self):
        """
            Gives the percentage of user who has done the challenge today
        """
        current_time = date.today()
        participants = self.participants.all()
        number_participants = len(participants)

        if number_participants == 0:
            return 0

        completed_user = ChallengeRecord.objects.filter(
            date=current_time,
            challenge = self,
            user__in = participants
        ).values_list('user', flat=True).distinct()

        total_completed = completed_user.count()
        return int((total_completed / number_participants) * 100)

    def streakGroup(self):
        """
            Returns the streak of the group. Even if one person has done it, 
            it is considered as streak
        """
        records = set(
            ChallengeRecord.objects
            .filter(challenge=self)
            .values_list('date', flat=True)
            )

        streak = 0
        time = date.today()

        while time in records:
            streak += 1
            time -= timedelta(days=1)
        
        return streak

    def topPeople(self):
        """
            Returns Top leader (10 user ids) who has done the most days.
        """
        top_leaders = (
            ChallengeRecord.objects
            .filter(challenge=self)
            .values('user')
            .annotate(days_done=Count('date'))
            .order_by('-days_done')
            .values('user')[:10]
        )

        return top_leaders


class ChallengeLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'challenge')

class ChallengeStatsIndividual(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    streak = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class ChallengeRecord(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('challenge', 'user', 'date')
    

class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_initiated')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_received')
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')
    
    def save(self, *args, **kwargs):
        # Avoid duplicate chats
        if self.user1.id > self.user2.id:
            self.user1, self.user2 = self.user2, self.user1

        if Chat.object.filter(user1=self.user1, user2=self.user2).exists():
            raise ValueError("Chat between users already exists!")

        super.save(*args, **kwargs)

class Settings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_settings')
    allow_messaging = models.BooleanField(default=True)
    has_whitelist = models.BooleanField(default=False)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=1000)
    sent_at = models.DateTimeField(auto_now_add=True)

class WhitelistPeople(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='whitelist_people')
    allowed_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='whitelisted_by')
    
    class Meta:
        unique_together = ('user', 'allowed_person')

    def clean(self):
        if self.user == self.allowed_person:
            raise ValidationError('One person cannot whitelist himself or herself. so do not try mess up with application')










