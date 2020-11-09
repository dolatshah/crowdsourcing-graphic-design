from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from freeDesigner.models import UserProfile


import datetime


class File(models.Model):    
	uploader=models.ForeignKey(UserProfile)
	description=models.CharField(max_length=500)
	uploadTime = models.DateTimeField()
	is_downloaded=models.BooleanField()
	path=models.CharField(max_length=500)


class Employee (models.Model):

	userprofile=models.ForeignKey(UserProfile)
	gainedMoney=models.IntegerField(max_length=11,null=True)
	cashedMoney=models.IntegerField(max_length=11,null=True)

	is_canceled=models.BooleanField(default=False)
	is_requested_for_complete=models.BooleanField(default=False)

	is_employee_online=models.BooleanField(default=False)
	is_employer_online=models.BooleanField(default=False)

	employerMax = models.IntegerField(default=0)
	employeeMax = models.IntegerField(default=0)

	rankTextForEmployee = models.CharField(max_length=1000)
	rankTextForEmployer = models.CharField(max_length=1000)


class Project(models.Model):
	employer=models.ForeignKey(UserProfile,related_name='employer')
	employee=models.OneToOneField(Employee,null=True,blank=True)


	offeringUsers=models.ManyToManyField(UserProfile,null=True,through='Offering',related_name='offeringUsers')


	choosedOffer_id=models.IntegerField(max_length=11,null=True,blank=True)

	files=models.ManyToManyField(File,null=True,blank=True)

	title=models.CharField(max_length=50)
	category=models.CharField(max_length=50)
	description=models.CharField(max_length=1000)

	startBid = models.CharField(max_length=20,null=True)
	endBid = models.CharField(max_length=20,null=True)

	startSlider = models.CharField(max_length=3,null=True)
	endSlider = models.CharField(max_length=3,null=True)

	employer_cashed_money=models.IntegerField(max_length=11,null=True)

	offerTime = models.DateTimeField()
	offerDay = models.IntegerField(max_length=3,null=True)
	startDate= models.DateTimeField(null=True,blank=True)
	endDate=models.DateTimeField(null=True,blank=True)
	hourTimeForOffer=models.IntegerField(null=True)

	is_active=models.BooleanField(default=True)
	is_running=models.BooleanField(default=False)
	is_failed=models.BooleanField(default=False)
	is_finished=models.BooleanField(default=False)
	is_canceled=models.BooleanField(default=False)
	is_public=models.BooleanField(default=True)

	########
	is_denied=models.BooleanField(default=False)
	########

	#sue part
	is_judgment=models.BooleanField(default=False)
	is_chat=models.BooleanField(default=False)
	employerRequestedMoneyForEnd=models.IntegerField(max_length=11,null=True,blank=True)
	employeeRequestedMoneyForEnd=models.IntegerField(max_length=11,null=True,blank=True)


	is_wait_for_employee=models.BooleanField()
	is_wait_for_employer=models.BooleanField()

	wait_for_employee_date=models.DateTimeField(null=True,blank=True)
	wait_for_employer_date=models.DateTimeField(null=True,blank=True)





class Offering (models.Model):

	offerer=models.ForeignKey(UserProfile)
	project=models.ForeignKey(Project)
	text=models.CharField(max_length=1000)
	#percentage=models.IntegerField(max_length=3)
	value=models.IntegerField(max_length=11)
	totallValue=models.IntegerField(max_length=11)
	bayane=models.IntegerField(max_length=11)
	offerTime = models.DateTimeField()
	offerDay = models.IntegerField(max_length=3)

	is_accepted_by_employer=models.BooleanField(default=False)
	is_accepted_by_employee=models.BooleanField(default=False)
	image=models.CharField(max_length=1000)

class Discussion(models.Model) :

	project = models.ForeignKey(Project)
	userprofile = models.ForeignKey(UserProfile)
	message = models.CharField(max_length=500)
	date = models.DateTimeField()


class ProjectFile(models.Model):
	project = models.ForeignKey(Project)
	uploadTime = models.DateTimeField()

