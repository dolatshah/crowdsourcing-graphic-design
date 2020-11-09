from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

import datetime
from datetime import timedelta

GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
)

ACTIVITY_CHOICES =(
        
        ('W','Withdraw'),
        ('C','Cash'),
        
)

    
 



class AccountActivity(models.Model):
    activityType = models.CharField(max_length=1, choices=ACTIVITY_CHOICES)
    transmitedMoney=models.IntegerField(max_length=11)
    transferTime=models.DateTimeField()
    description=models.CharField(max_length=100)

    
class Account(models.Model):
    bankName=models.CharField(max_length=50,null=True,blank=True)
    kardNumber=models.CharField(max_length=20, null=True,blank=True)
    accountActivity=models.ManyToManyField(AccountActivity,null=True)
    money=models.IntegerField(max_length=11,blank=True)
    is_verified=models.BooleanField()


class projectsForOffer(models.Model):
    is_crowd=models.BooleanField()
    project_id=models.IntegerField(max_length=11)
    

class relatedProjects(models.Model):
    is_crowd=models.BooleanField()
    project_id=models.IntegerField(max_length=11)
    is_employer=models.BooleanField()


class Chat(models.Model):

    text = models.CharField(max_length=250)
    date = models.DateTimeField(blank=True)    
    otherSideUser = models.ForeignKey(User,blank=True)
    is_read = models.NullBooleanField()
    is_sender = models.BooleanField()
    

class Resume(models.Model):    
    description=models.CharField(max_length=500)
    uploadTime = models.DateTimeField()
    is_downloaded=models.BooleanField()
    path=models.CharField(max_length=500)

    

class UserProfile(models.Model):
    
    user = models.OneToOneField(User, db_index=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,null=True,blank=True)
    birthday = models.DateField(null=True,blank=True)
    
    mobile = models.CharField(max_length=20, null=True, blank=True)
    
    chats = models.ManyToManyField(Chat,null=True,blank=True)
    
    totalRank=models.IntegerField(max_length=11,null=True)
    
    account=models.OneToOneField(Account,null=True)
    
    text=models.CharField(max_length=500,null=True,blank=True)
    address=models.CharField(max_length=500,null=True,blank=True)
    is_ban=models.BooleanField(default=False)
    is_ranked=models.BooleanField(default=False)
    is_email_verified=models.BooleanField(default=False)
    is_admin=models.BooleanField(default=False)

    is_subscribeForProjects = models.BooleanField(default=True)
    is_subscribeForNotif = models.BooleanField(default=True)

    files=models.ManyToManyField(Resume,null=True,blank=True)

    relatedProjects = models.ManyToManyField(relatedProjects,blank=True)
    projectsForOffer = models.ManyToManyField(projectsForOffer,blank=True)

    invitor_id = models.IntegerField(max_length=11,null=True,blank=True)


    is_image_uploaded = models.BooleanField(default=False)

    is_designer = models.NullBooleanField(null=True,blank=True)



class Message(models.Model):
    sender = models.ForeignKey(UserProfile,related_name='sender')
    receiver= models.ForeignKey(UserProfile,related_name='receiver')
    text=models.CharField(max_length=1000)
    sentTime = models.DateTimeField()
    is_read = models.NullBooleanField()
    is_private = models.NullBooleanField()
    project_id=models.IntegerField(max_length=11,null=True)
    


class Notification(models.Model):
    sender = models.CharField(max_length=15)
    receiver= models.ForeignKey(UserProfile)
    text=models.CharField(max_length=1000)
    sentTime = models.DateTimeField()
    is_read = models.NullBooleanField()



    

