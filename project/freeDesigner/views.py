#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#encoding:UTF-8
import os, sys

from django.db.models import get_app, get_models
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.shortcuts import render, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from freeDesigner.forms import RegisterForm,LoginForm,MessageForm,AccountForm,photoForm
from freeDesigner.models import UserProfile,Message,Account,AccountActivity,relatedProjects,Notification,Chat,Resume
from project.models import Project,Employee,Offering
from django.db.models import Count
from django.db.models import Q
from django.contrib import auth
import hashlib
from django.utils.timezone import utc,LocalTimezone

#from mysite.forms import ContactForm
import datetime
from PIL import Image

import MySQLdb
from django.utils.dateformat import DateFormat, TimeFormat
import warnings
warnings.filterwarnings('error', r"DateTimeField .* received a naive datetime",RuntimeWarning, r'django\.db\.models\.fields')



def main(request):
	
	form={}
#	form['employeeRankList'] = employeeRankList.objects.all().order_by('rank')[:4]
#	form['employerRankList'] = employerRankList.objects.all().order_by('rank')[:4]
	
	if request.user.is_authenticated():
		form['login']=True
		form['user']=request.user
		return render_to_response('main.html' , {'form':form})
	else:
		form['login'] = False
		return render_to_response('main.html' , {'form': form })


def other(request,username):

	form={}

	try:
		view=User.objects.get(username=username)
		form['view']=view
		userprofile=view.userprofile

	except:
		return render_to_response('alert.html', {'error':"کاربری با این نام وجود نداردعهنتبمن",'address':'0'})


	if request.user.is_authenticated():
		try:
			if userprofile==request.user.userprofile:
				return HttpResponseRedirect("/profile/")
		except:
			return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/'})

		user=User.objects.get(id=request.user.id)
		form['user']=user
		form['login']=True

	else:
		form['login']=False
		form['new']=view


	employerProjects=[]
	employeeProjects=[]
	projectsForOffer=[]

	import operator



	for related in userprofile.relatedProjects.all():
		if not related.is_crowd:
			try:
				project=Project.objects.get(id=related.project_id)
			except:
				break
			if related.is_employer:
				if not project in employerProjects:
					if project.employer == userprofile:
						employerProjects.append(project)
						continue
			else:
				if not project in employeeProjects:
					if project.employee:
						if project.employee.userprofile == userprofile:
							employeeProjects.append(project)
							continue


	form['employerProjects']=employerProjects
	form['employeeProjects']=employeeProjects
	form['skills']=userprofile.skill.all()
	form['resumes'] = userprofile.files

	try:
		form['employerTotalRank']=userprofile.rankForEmployer.totalRank / 5
	except:
		form['employerTotalRank']= -1

	try:
		form['employeeTotalRank']=userprofile.rankForEmployee.totalRank / 5
	except:
		form['employeeTotalRank']= -1



	try:
		form['employeePoint']= employeeRankList.objects.get(userprofile=userprofile).rank
	except:
		ranklist=employeeRankList(userprofile=userprofile,point=0,rank=userprofile.id)
		ranklist.save()
		form['employeePoint']= employeeRankList.objects.get(userprofile=userprofile).rank

	try:
		form['employerPoint']= employerRankList.objects.get(userprofile=userprofile).rank
	except:
		ranklist=employerRankList(userprofile=userprofile,point=0,rank=userprofile.id)
		ranklist.save()
		form['employerPoint']= employerRankList.objects.get(userprofile=userprofile).rank




	if request.user.is_authenticated():
		return render_to_response('profileForOthers.html', {'login':True,'form': form ,'userprofile':userprofile,'user':user},context_instance=RequestContext(request))
	else:
		return render_to_response('profileForOthers.html', {'form': form ,'userprofile':userprofile,'login':False},context_instance=RequestContext(request))

def profile(request,tabId=0):
	if request.user.is_authenticated():



		form={'login': True,'user':request.user }

		try:
			userprofile=UserProfile.objects.get(id=request.user.id)
		except:
			return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/profile/'})

		employerProjects=[]
		employeeProjects=[]
		projectsForOffer=[]

		import operator




		projects={}

		for related in userprofile.projectsForOffer.all():
			
			try:
				project=Project.objects.get(id=related.project_id)
	
				if not project.is_running:
					projects[project]= datetime.timedelta(hours=project.hourTimeForOffer) + project.offerTime -date.now()#.replace(tzinfo=utc)
			except:
				pass
			
		projectsForOffer = sorted(projects.iteritems(), key=operator.itemgetter(1))[:20]


		for related in userprofile.relatedProjects.all():
			if not related.is_crowd:
				try:
					project=Project.objects.get(id=related.project_id)
					if related.is_employer:
						if not project in employerProjects:
							if project.employer == userprofile:
								employerProjects.append(project)
								continue
					else:
						if not project in employeeProjects:
							if project.employee:
								if project.employee.userprofile == userprofile:
									employeeProjects.append(project)
									continue
				except:
					pass


		form['employerProjects']=employerProjects
		form['employeeProjects']=employeeProjects

		form['projectsForOffer']=projectsForOffer

		form['resume']=userprofile.files
		if userprofile.is_designer:
			form['is_designer']="پیمانکار"
		else:
			form['is_designer']="کارفرما"

		form['userprofile']=userprofile
		if userprofile.is_image_uploaded:
			form['image_id']=userprofile.id
		else:
			form['image_id']=0
		form['user_username']=request.user.username
		form['last_login']=request.user.last_login
		if tabId!=0:
			form['tabId']=tabId

		return render_to_response('profile2.html' ,{'form':form})
	else:
		return HttpResponseRedirect("/")





def editProfile(request):
	
	userprofile=UserProfile.objects.get(id=request.user.id)
	

	if request.user.is_authenticated():

		user = User.objects.get(id=request.user.id)
		userprofile=UserProfile.objects.get(user=user)

		form={'login': True,'user':request.user}
	else:
		return HttpResponseRedirect("/")


	if request.method == 'POST':



		
		if request.FILES:

			f=request.FILES["f"]
			
			if f.size > 4*1024*1024:
				string="<script type='text/javascript '> window.alert ('Image file too large ( > 4mb )' );window.location.href= '/editProfile/';</script>"
				return HttpResponse(string)
			
			dest="static/files/profile/"+str(userprofile.id)+".jpg"

			with open(dest, 'wb+') as destination:
				for chunk in f.chunks():
					destination.write(chunk)
			

			userprofile.is_image_uploaded = True



		
		if request.POST.get('firstname'):
			user.first_name=request.POST.get('firstname')

		if request.POST.get('lastname'):
			user.last_name=request.POST.get('lastname')

		if request.POST.get('birthday'):

			
			try:
				userprofile.birthday = datetime.datetime.strptime(request.POST.get('birthday'), "%Y/%m/%d")
			except:
				return render_to_response('alert.html', {'error':"خطا در پر کردن فرم",'address':'/editProfile/'})

		if request.POST.get('mobile'):
			userprofile.mobile=request.POST.get('mobile')

		if request.POST.get('birthday'):
			userprofile.mobile=request.POST.get('mobile')

		if request.POST.get('desc'):
			userprofile.text=request.POST.get('desc')

		if request.POST.get('address'):
			userprofile.address=request.POST.get('address')




		user.save()
		userprofile.save()

		



		

		


		

		

	
		
		
		


		
		

		

		return HttpResponseRedirect("/editProfile/")

	elif request.method == 'GET':

		



		categories={}

		

		#print categories
		


		
		#userprofile=UserProfile.objects.get(id=request.user.id)


		
		#set3=user.education.all()
		checked2=[]
		

		


		form={}
		if userprofile.is_image_uploaded:
			form['image_id']=userprofile.id
		else:
			form['image_id']=0
		form['user_name']=userprofile.user.username
		form['last_login']=userprofile.user.last_login
		form['photo'] = photoForm()
		form['firstname']=user.first_name
		form['lastname']=user.last_name
		form['categories'] = categories
		if userprofile.birthday:
			month = str(userprofile.birthday.month)
			if len(month)==1:
				month= '0'+month

			day = str(userprofile.birthday.day)
			if len(day)==1:
				day = '0'+day
			
			birthday=str(userprofile.birthday.year)+"/"+month+"/"+day
			form['birthday']=birthday
		if userprofile.mobile:
			form['mobile']=userprofile.mobile
		else:
			form['mobile']='09'

		if userprofile.gender:
			form['gender']=userprofile.gender
		form['desc']=userprofile.text
		form['address']=userprofile.address






		
		



		return render_to_response('editProfile.html', {'login':True ,'form':form},context_instance=RequestContext(request))


	return render_to_response('editProfile.html', {'login':True},context_instance=RequestContext(request))



def signup(request,invitor):
	
	if request.method == 'POST' :
		form = RegisterForm(request.POST)
		if form.is_valid():

			cd = form.cleaned_data
			email = cd['email'] #TODO: Email should be unique
			user_name=cd['user_name']
			user = User.objects.create_user(username = user_name, password = cd['password'], email = cd['email'])
			user.save()

			account=Account(money=0,is_verified=False)
			account.save()

			userProfile = UserProfile(id=user.id,user_id=user.id,totalRank=0
									,account=account,is_image_uploaded=False,is_ban=False,is_email_verified=False)
			
			if request.POST.get('is_designer'):
				if request.POST.get('is_designer')== 'f':
					userProfile.is_designer=False
				else:
					userProfile.is_designer=True
					
			if (request.session.get('invitor_id')):
				userProfile.invitor_id=request.session.get('invitor_id')
				del request.session['invitor_id']
			userProfile.save()

			userProfile.is_email_verified = True
			userProfile.save()
			return render_to_response('alert.html', {'error':"عملیات  ثبت نام با موفقیت انجام شد",'address':'/login/'})
			

		else:
			return render_to_response('signup.html', {'form':form},context_instance=RequestContext(request))
		

		
	elif request.method == 'GET':
		
		
		if (invitor):
			try:
				UserInvitor=User.objects.get(username=invitor)
			except:
				return render_to_response('alert.html', {'error':"کاربری با این نام وجود ندارد",'address':'0'})

		form = RegisterForm()
		return render_to_response('signup.html', {'form':form},context_instance=RequestContext(request))
	else:
		form = RegisterForm()
		return render_to_response('signup.html', {'form':form},context_instance=RequestContext(request))




def register(request,invitor):
	
	if request.method == 'POST' :
		form = RegisterForm(request.POST)
		
		
		if form.is_valid():

			cd = form.cleaned_data
			email = cd['email'] #TODO: Email should be unique
			user_name=cd['user_name']
			user = User.objects.create_user(username = user_name, password = cd['password'], email = cd['email'])
			user.save()

			contactFilter(user.username,"username",user.id)

			account=Account(money=0,is_verified=False)
			account.save()

			userProfile = UserProfile(email = cd['email'],id=user.id,user_id=user.id,totalRank=0
									,account=account,is_image_uploaded=False,is_ban=False,is_email_verified=False)
			
			if (request.session.get('invitor_id')):
				userProfile.invitor_id=request.session.get('invitor_id')
				del request.session['invitor_id']
			userProfile.save()

			ranklist=employeeRankList(userprofile=userProfile,point=0,rank=userProfile.id)
			ranklist.save()

			ranklist=employerRankList(userprofile=userProfile,point=0,rank=userProfile.id)
			ranklist.save()
			

			
			import hashlib
			m=hashlib.md5()
			m.update(str(user.username) + str(user.id) + str(user.email) )
			#print m.hexdigest()
			try:
				mail(userId=user.id,kind="verify",text=str(m.hexdigest())) 
			except Exception as e: 
				print("register email error : "+ str(e) + " " + str(date.now()) )
				
			####################
			#userProfile.is_email_verified = True
			#userProfile.save()
			#return render_to_response('alert.html', {'error':"عملیات  ثبت نام با موفقیت انجام شد",'address':'/login/'})
			####################
			
			return render_to_response('registered.html', {'username':user.username},context_instance=RequestContext(request))

		else:
			return render_to_response('register.html', {'form':form},context_instance=RequestContext(request))
		
		
	elif request.method == 'GET':
		
		
		if (invitor):
			try:
				UserInvitor=User.objects.get(username=invitor)
			except:
				return render_to_response('alert.html', {'error':"کاربری با این نام وجود ندارد",'address':'0'})

		form = RegisterForm()
		return render_to_response('register.html', {'form':form},context_instance=RequestContext(request))
	else:
		form = RegisterForm()
		return render_to_response('register.html', {'form':form},context_instance=RequestContext(request))



def login_view(request,redirect=0):
	if str(redirect)=="redirect":
		link = request.GET.get('next')[1:-1]
		return render_to_response('alert.html', {'error':"ابتدا باید وارد شوید",'address':'/login/'+link+'/'})
	if request.method == 'POST':

		form = LoginForm(request.POST)
		if form.is_valid():
			username = request.POST.get('username', '')
			password = request.POST.get('password', '')
			
			if '@' in username :
				try:
					username = User.objects.get(email = username).username
				except:
					form.errors="لطفا ابتدا وارد لینک فعال سازی که به ایمیلتان فرستاده شده است , شوید"
					return render_to_response('login.html', {'form':form},context_instance=RequestContext(request))
				
				
			user = auth.authenticate(username=username, password=password)
			
			if user is not None and user.is_active:
				auth.login(request, user)
				return HttpResponseRedirect("/controlPanel/")

			else:
				form.errors="نام کاربری یا رمز عبور اشتباه است"
				return render_to_response('login.html', {'form':form},context_instance=RequestContext(request))
		else:
			# Show an error page
			return render_to_response('login.html', {'form':form},context_instance=RequestContext(request))

	elif request.method == 'GET':
		#TODO: Initial return page's fields

		form = LoginForm(
			# initial = {'username': 'initial'}
		)



		return render_to_response('login.html', {'form':form},context_instance=RequestContext(request))
	else:
		form = LoginForm(request.POST)
		return render_to_response('login.html', {'form':form},context_instance=RequestContext(request))



def logout_view(request):
	auth.logout(request)
	# Redirect to a success page.
	return HttpResponseRedirect("/")







def message(request,receiver_id):

	if request.user.is_authenticated():

		senderprofile=UserProfile.objects.get(id=request.user.id)
		receiverprofile=UserProfile.objects.get(id=receiver_id)

		if request.method == 'POST':
			form = MessageForm(request.POST)
			if form.is_valid():

				is_allowed = True


				cd = form.cleaned_data
				text=cd['text']
				message=Message(receiver=receiverprofile,sender=senderprofile,text=unicode(text),sentTime=datetime.datetime.now().replace(tzinfo=utc))
				message.save()
				return render_to_response('alert.html', {'error':"پیغام فرستاده شد",'address':'-1'},content_type='text/html; charset=utf-8')

			else:
				return render_to_response("message.html", {'form': form,'login':True},context_instance=RequestContext(request))

		if request.method == 'GET':

			form=MessageForm()
			form.receiver=receiverprofile
			form.user=request.user


			return render_to_response("message.html", {'form': form,'login':True},context_instance=RequestContext(request))


	else:
		return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/'})



def account(request,tabId=0):
	if request.user.is_authenticated():
		userprofile=UserProfile.objects.get(id=request.user.id)
		
		form={'user':userprofile,'login':True}

		#account=Account.objects.get(userprofile=userprofile)
		account=userprofile.account



		if request.method == 'GET':
			form['account']=account
			if tabId!=0:
				form['tabId']=tabId
			form['user_username']=request.user.username	
			form['user_money']=userprofile.account.money

			return render_to_response("account.html", {'form': form},context_instance=RequestContext(request))

		if request.method=='POST':
			userprofile.account.bankName = request.POST.get('bank-name')
			userprofile.account.kardNumber = request.POST.get('card-number')
			userprofile.account.save()
			userprofile.save()
			return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':'/account/'})

		


	else:
		return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/'})
	
	return render_to_response('account.html' ,{'form':form})

	




def deposit (request,is_verified=0):
	
	if request.user.is_authenticated():

		userprofile=UserProfile.objects.get(id=request.user.id)

		#account=Account.objects.get(userprofile=userprofile)
		account=userprofile.account

		form=AccountForm()
		form.user=userprofile
		form.login=True
		form.account=account

		
		if request.method == 'GET':
			#print "deposit get"
			return render_to_response("deposit.html", {'form': form,'login':True,'user':userprofile},context_instance=RequestContext(request))

		if request.method == 'POST' :			

			form = AccountForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data

				money=cd['text']
				try:
					if int(money) < 1000:
						return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':'-1'})
					
				except:
					return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':'-1'})
				
				account.money=str(int(account.money)+int(money))
				activity=AccountActivity(activityType='C',transmitedMoney=money,transferTime=datetime.datetime.now().replace(tzinfo=utc),description='deposit')
				activity.save()
				account.accountActivity.add(activity)
				account.save()

				

				return HttpResponseRedirect("/account")				
				
			else:
				return render_to_response("deposit.html", {'form': form , 'login':True,'user':userprofile },context_instance=RequestContext(request))

		
			

	else:
		return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/'})

			
			
		 	
	

def withdraw (request):

	if request.user.is_authenticated():

		userprofile=UserProfile.objects.get(id=request.user.id)

		#account=Account.objects.get(userprofile=userprofile)
		account=userprofile.account

		form=AccountForm()
		form.user=userprofile
		form.login=True
		form.account=account

		if request.method == 'GET':

			return render_to_response("withdraw.html", {'form': form},context_instance=RequestContext(request))

		if request.method == 'POST':			
			form = AccountForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data
				money=cd['text']

				if int(money)/10>int(account.money):
					return render_to_response('alert.html', {'error':"حساب کاربری شما دارای اعتبار کافی نمیباشد",'address':'/account/'})
				else:

					
					

					account.money=str(int(account.money)-int(money))
					activity=AccountActivity(activityType='W',transmitedMoney=money,transferTime=datetime.datetime.now().replace(tzinfo=utc),description='withdraw')
					activity.save()
					account.accountActivity.add(activity)
					account.save()

					return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':'/account/'})
			else:
				return render_to_response("withdraw.html", {'form': form},context_instance=RequestContext(request))



	else:
		return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/'})



@login_required
def messagesList(request):
	userprofile=UserProfile.objects.get(id=request.user.id)

	receiverMessages=Message.objects.filter(receiver=userprofile).order_by('sentTime').reverse()

	inbox={}
	senders=[]

	for message in receiverMessages:
		message.is_read=True
		message.save()
		if message.sender not in senders:
			senders.append(message.sender)
			inbox[message.sender]=message


	senderMessages=Message.objects.filter(sender=userprofile).order_by('sentTime').reverse()

	sent={}
	receivers=[]

	for message in senderMessages:
		if message.receiver not in receivers:
			receivers.append(message.receiver)
			sent[message.receiver]=message




	form={}
	form['inbox']=inbox
	form['sent']=sent
	return render_to_response("messagesList.html", {'form': form,'login':True,'user':userprofile},context_instance=RequestContext(request))


@login_required
def notifications(request):
	userprofile=UserProfile.objects.get(id=request.user.id)

	for notif in Notification.objects.filter(receiver=userprofile):
		notif.is_read=True
		notif.save()


	notifications=Notification.objects.filter(receiver=userprofile).order_by('sentTime').reverse()


	form={}
	form['messages']=notifications
	return render_to_response("MyNotification.html", {'form': form,'login':True,'user':userprofile},context_instance=RequestContext(request))
	


@login_required
def conversation(request,messageid):

	userprofile=UserProfile.objects.get(id=request.user.id)

	message=Message.objects.get(id=messageid)

	receiver=message.receiver
	sender=message.sender

	messages=Message.objects.filter(Q(sender=sender,receiver=receiver) | Q(sender=receiver,receiver=sender)).order_by('sentTime')

	if request.method=="GET":
		
		form={}
		
		if receiver == userprofile:
			form['other']=sender.user.username
		else:
			form['other']=receiver.user.username
			
		form['messages']=messages
		form['messageid']=messageid
		form['user']=userprofile.user

		return render_to_response("conversation.html", {'form': form,'login':True,'user':userprofile},context_instance=RequestContext(request))

	if request.method=="POST":

		text=request.POST.get('text')
		if sender==userprofile:

			m=Message(sender=userprofile,receiver=receiver,text=unicode(text),sentTime=datetime.datetime.now().replace(tzinfo=utc),is_read=False)
			m.save()
		else:

			m=Message(sender=userprofile,receiver=sender,text=unicode(text),sentTime=datetime.datetime.now().replace(tzinfo=utc),is_read=False)
			m.save()
			
		#print date.now()
		st = "/conversation/"+str(messageid)+"/"
		#return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':st},content_type='text/html; charset=utf-8')
		return HttpResponseRedirect(st)






@login_required
def controlPanel(request,tabId=0):

	try:
		userprofile=UserProfile.objects.get(id=request.user.id)
	except:
		return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/controlPanel/'})

	
	form={}
	if tabId!=0:
		form['tabId']=tabId



	
	
	projectsForOffer=[]
	
	projectsForOffer=[]
	import operator
	projects={}
	
	for related in userprofile.projectsForOffer.all():
		try:
			project=Project.objects.get(id=related.project_id)

			#if not project.is_running:
			projects[project]= datetime.timedelta(hours=project.hourTimeForOffer) + project.offerTime -date.now()#.replace(tzinfo=utc)
		except:
			pass

	projectsForOffer = sorted(projects.iteritems(), key=operator.itemgetter(1))[:20]

	form['projectsForOffer']=projectsForOffer


	affers={}
	
	form['userprofile']=userprofile
	if userprofile.is_image_uploaded:
		form['image_id']=userprofile.id
	else:
		form['image_id']=0
	
	for affer in UserProfile.objects.filter(invitor_id=userprofile.id):
		affers[affer]=False
		for relatedProject in affer.relatedProjects.all():
			project = Project.objects.get(id=relatedProject.project_id)
			if project.is_finished:
				affers[affer]=True
				break
		
			  
	form['affers']=affers
	form['lastlogin']=userprofile.user.last_login

	if userprofile.is_designer:
		return render_to_response("ControlPanelForDesigner.html", {'form': form,'login':True,'userprofile':userprofile},context_instance=RequestContext(request))
	else:
		return render_to_response("ControlPanelForEmployer.html", {'form': form,'login':True,'userprofile':userprofile},context_instance=RequestContext(request))

@login_required
def myProjects(request):

	form={'login': True,'user':request.user }
	userprofile=UserProfile.objects.get(id=request.user.id)
	#messages=Message.objects.filter(receiver=userprofile)
	#form['messages']=messages

	employerProjects=[]
	employeeProjects=[]

	#projectsForOffer=userprofile.projectsForOffer.all().order_by('sentTime').reverse()[:20]


	for related in userprofile.relatedProjects.all():
		if not related.is_crowd:
			try:
				project=Project.objects.get(id=related.project_id)
				if related.is_employer:
					if not project in employerProjects:
						employerProjects.append(project)
						continue
				else:
					if not project in employeeProjects:
						employeeProjects.append(project)
						continue
			except:
				pass


	form['employerProjects']=employerProjects
	form['employeeProjects']=employeeProjects
	#form['projectsForOffer']=projectsForOffer



	return render_to_response('myProjects.html' ,{'form':form})


from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def chat(request,otherSideId,projectId):

	otherSide=UserProfile.objects.get(id=otherSideId)

	form={}
	
	form['otherSideUser']=otherSide.user

	userprofile=UserProfile.objects.get(id=request.user.id)

	project=Project.objects.get(id=projectId)

	if project.employer == userprofile:
		lastMessageId = project.employee.employerMax
	else:
		lastMessageId = project.employee.employeeMax

	form['max']=lastMessageId


	if request.method == "POST":
		


		text=request.POST.get('text')


		sender=request.user.userprofile

		#contactFilter(text,"chat ,sender",sender.id)

		forSender = Chat()

		forSender.text=text
		forSender.otherSideUser=otherSide.user
		forSender.date = datetime.datetime.now().replace(tzinfo=utc)
		forSender.is_read = True
		forSender.is_sender = True
		forSender.save()

		sender.chats.add(forSender)
		sender.save()



		forReceiver = Chat()
		forReceiver.otherSideUser=sender.user
		forReceiver.text=text
		forReceiver.date = datetime.datetime.now().replace(tzinfo=utc)


		forReceiver.is_read = False
		forReceiver.is_sender = False
		forReceiver.save()

		otherSide.chats.add(forReceiver)
		otherSide.save()



		string = '/chat/'+ otherSideId
		#return HttpResponseRedirect(string)
		return HttpResponse("done")


	if request.method == "GET":
		
		first=otherSide
		second=request.user.userprofile

		#print first.user.username,first.user.is_authenticated()
		#print second.user.username,second.user.is_authenticated()
		
		
		messages = second.chats.filter(otherSideUser=first).order_by('date')
		
		
		if project.employer == userprofile:
					
			lastMessageId = project.employee.employerMax
		
			ma=int(lastMessageId)
			
			
			counter=0
					
			for m in messages:
					
				m.is_read = True
				m.save()
				counter+=1
				if counter == messages.count():
					ma=m.id
			
			
			project.employee.employerMax=ma
			project.employee.save()
			project.save()


		else:
			lastMessageId = project.employee.employeeMax

			ma=int(lastMessageId)
			counter=0

			for m in messages:

				m.is_read = True
				m.save()
	
				counter+=1
				if counter == messages.count():
					ma=m.id


			
			
			project.employee.employeeMax=ma
			project.employee.save()
			project.save()


		form['year']=datetime.datetime.now().replace(tzinfo=utc).year
		form['day']=datetime.datetime.now().replace(tzinfo=utc).day
		form['month']=datetime.datetime.now().replace(tzinfo=utc).month
		form['hour']=datetime.datetime.now().replace(tzinfo=utc).hour
		form['minute']=datetime.datetime.now().replace(tzinfo=utc).minute
		form['second']=datetime.datetime.now().replace(tzinfo=utc).second

		return render_to_response('chat.html', {'form':form ,'login':True,'messages':messages,'user':request.user.userprofile,'other':otherSide,'projectId':projectId}, context_instance=RequestContext(request))


@login_required
def chats(request,first,second,projectId):

	#print "start"
	#from itertools import chain


	first=User.objects.get(id=first)
	second=UserProfile.objects.get(id=second)

	myStatus=otherStatus="offline"
	project=Project.objects.get(id=projectId)

	userprofile=UserProfile.objects.get(id=request.user.id)


	if project.employer == userprofile:
		lastMessageId = project.employee.employerMax
		if project.employee.is_employer_online :
			myStatus = "online"

		if project.employee.is_employee_online :
			otherStatus = "online"



		messages = second.chats.filter(otherSideUser=first,id__gt=int(lastMessageId)).order_by('date')

		

		ma=int(lastMessageId)
		counter=0
		for m in messages:
			m.is_read = True
			m.save()

			counter+=1
			if counter == messages.count():
				ma=m.id
		
		
		
		project.employee.employerMax=ma
		project.employee.save()
		project.save()


	else:
		#print "2"
		lastMessageId = project.employee.employeeMax

		if project.employee.is_employee_online :
			myStatus = "online"

		if project.employee.is_employer_online :
			otherStatus = "online"

		messages = second.chats.filter(otherSideUser=first,id__gt=int(lastMessageId)).order_by('date')

		#print "last2",lastMessageId

		#print "count2",messages.count()

		ma=int(lastMessageId)
		counter=0

		for m in messages:

			m.is_read = True
			m.save()

			counter+=1
			if counter == messages.count():
				ma=m.id


			
		project.employee.employeeMax=ma
		project.employee.save()
		project.save()




	#print "count",messages.count()
	#print "last",lastMessageId
	#form['max']=lastMessageId

	#firstMessages = first.chats.all()[:3]

	#messages = list(chain(firstMessages,secondMessages))

	#print lastMessageId
	if messages.count()>0:
		return render_to_response('messages.html', {'messages': messages ,'max':lastMessageId,'myStatus':myStatus,'otherStatus':otherStatus})
	else:
		st="none<div value='maximum' class='"+str(lastMessageId)+"' data='"+str(myStatus)+"||"+str(otherStatus)+"' ></div>"
		#<div value="maximum" class="{{max}}" data="{{myStatus}}||{{otherStatus}}" ></div>
		return HttpResponse(st)


@login_required
def resume(request):

	userprofile = UserProfile.objects.get(id=request.user.id)

	if request.method == "GET":

		form={}
		form['resumes'] = userprofile.files
		return render_to_response('Resume2.html', {'login': True, 'form': form}, context_instance=RequestContext(request))
	elif request.method == "POST":
	
		f=request.FILES['myfile']

		description=request.POST.get('description')
	
		myfile=Resume(description=description,uploadTime=datetime.datetime.now().replace(tzinfo=utc),path="static/resume/",is_downloaded=False)
		myfile.save()
	
	


	
		dest="static/resume/"+str(myfile.id)+".zip"
	
		userprofile.files.add(myfile)
		userprofile.save()

	with open(dest, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

	return HttpResponseRedirect('/resume/')


def resume2(request,username):

	view=User.objects.get(username=username)

	userprofile = UserProfile.objects.get(id=view.id)


	if request.method == "GET":
		form={}
		form['resumes'] = userprofile.files
		return render_to_response('resume.html', {'login': False, 'form': form}, context_instance=RequestContext(request))



#from django.utils import simplejson
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def uploadResume(request):

	userprofile = UserProfile.objects.get(id=request.user.id)

	f=request.FILES['myfile']

	description=request.POST.get('description')

	myfile=Resume(description=description,uploadTime=date.now(),path="static/resume/",is_downloaded=False)
	myfile.save()

	contactFilter(myfile.description,"resume description",myfile.id)



	dest="static/resume/"+str(myfile.id)+".zip"

	userprofile.files.add(myfile)
	userprofile.save()

	with open(dest, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

	return HttpResponse(simplejson.dumps(myfile.id))

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def deleteResume(request):

	userprofile = UserProfile.objects.get(id=request.user.id)

	fileid=request.POST.get('name')

	myfile=Resume.objects.get(id=fileid)

	userprofile.files.remove(myfile)
	userprofile.save()
	myfile.delete()

	return HttpResponse(simplejson.dumps("done"))

@login_required
def removeResume(request,fileid):

	userprofile = UserProfile.objects.get(id=request.user.id)

	myfile=Resume.objects.get(id=fileid)

	userprofile.files.remove(myfile)
	userprofile.save()
	myfile.delete()


	dest="static/resume/"+str(fileid)+".zip"
	if os.path.isfile(dest):
		os.remove(dest)
	else:
		print("remove resume not found file id : "+ str(fileid) + " " + str(date.now()) )

	return HttpResponseRedirect('/profile/resumetab/')


def user_invite(request,invitor):
	
	try:
		view=User.objects.get(username=invitor)
		request.session['invitor'] = invitor

	except:
		return HttpResponseRedirect("/")



	if request.user.is_authenticated():
		return render_to_response('alert.html', {'error':"عملیات دعوت فقط برای کاربران ثبت نام نکرده میباشد",'address':'/profile/'})

	else:
		return HttpResponseRedirect("/")



def project_invite(request,invitor,projectId):
	
	string="/project/"+str(projectId)
	
	try:
		view=User.objects.get(username=invitor)
		request.session['invitor'] = invitor

	except:
		return HttpResponseRedirect(string)



	if request.user.is_authenticated():
		return render_to_response('alert.html', {'error':"عملیات دعوت فقط برای کاربران ثبت نام نکرده میباشد",'address':string})

	else:
		return HttpResponseRedirect(string)


def check_user(request,user):

	if (len(user)<5 	   or
		user.find('/')!=-1 or
		user.find('&')!=-1 or
		user.find('#')!=-1 or
		user.find('%')!=-1 or
		user.find('*')!=-1 or
		user.find('@')!=-1 or
		user.find('$')!=-1 or
		user.find('^')!=-1 or
		user.find(')')!=-1 or
		user.find('(')!=-1 or
		user.find('!')!=-1 or
		user.find("'")!=-1 or
		user.find("edit")!=-1 or
		user.find("roject")!=-1 or
		user.find("chat")!=-1 or
		user.find("esume")!=-1 or
		user.find("file")!=-1 or
		user.find("upload")!=-1 or
		user.find("delete")!=-1 or
		user.find("message")!=-1 or
		user.find("rofile")!=-1 or
		user.find("log")!=-1 or
		user.find("increase")!=-1 or
		user.find("ffer")!=-1 or
		user=='signup' or
		user=='register' or
		user=='account' or
		user=='deposit' or
		user=='withdraw' or
		user=='share' or
		user=='notifications' or
		user=='conversation' or
		user=='controlPanel' or
		user=='rank' or
		user=='done' or
		user=='setting' ):

		return HttpResponse("no")	
	try:
		User.objects.get(username=user)
		return HttpResponse("no")
	except:
		return HttpResponse("yes")
	
def check_mail(request,user):
	
	if user.find('@')== -1 or user.find('www')!=-1:
		return HttpResponse("no")

	try:
		User.objects.get(email=user)
		return HttpResponse("no")
	except:
		return HttpResponse("yes")
	

def forget(request):
	
	import random
	import string
	digits = "".join( [random.choice(string.digits) for i in xrange(5)] )
	chars = "".join( [random.choice(string.letters) for i in xrange(5)] )
	new = chars+digits
	
	if request.user.is_authenticated():
		
		user = request.user
		
		if request.method == "GET":
			return render_to_response('forget.html',{'login': True, 'user': user}, context_instance=RequestContext(request))
		
		if request.method == "POST":
			
			
			userprofile = UserProfile.objects.get(id=user.id)
			userprofile.user.set_password(new)
			user.save()
			userprofile.save()
			
			st = 'New PassWord : ' + new
			
			try:
				mail(userId=user.id,kind="forget",text= st ) 
			except Exception as e: 
				print("forget email error (login) :  "+ str(e) + " " + str(date.now()) )
			
			return render_to_response('forget.html', {'login': True, 'done':True , 'user': user , 'username':user.username},context_instance=RequestContext(request))

	else:
		
		if request.method == "GET":
			return render_to_response('forget.html', context_instance=RequestContext(request))
		
		if request.method == "POST":
			
			ail = request.POST.get('ail')
			
			try:
				user = User.objects.get(email = ail)
			except:
				return render_to_response('forget.html', {'login': False , 'done2':True },context_instance=RequestContext(request))
			
			userprofile = UserProfile.objects.get(id=user.id)
			userprofile.user.set_password(new)
			user.set_password(new)
			user.save()
			userprofile.save()
			
			st = 'New PassWord : ' + new



			try:
				mail(userId=user.id,kind="forget",text= st ) 
			except Exception as e: 
				print("forget email error (loguot) : "+ str(e) + " " + str(date.now()) )
				
			return render_to_response('forget.html', {'login': False , 'done':True },context_instance=RequestContext(request))
			
		



def send_verification(request):
	
	
	if request.user.is_authenticated():
		
		user = request.user
		
		if request.method == "GET":
			return render_to_response('send_verification.html',{'login': True, 'user': user}, context_instance=RequestContext(request))
		
		if request.method == "POST":
			
			import hashlib
			m=hashlib.md5()
			m.update(str(user.username) + str(user.id) + str(user.email) )
			try:
				mail(userId=user.id,kind="verify",text=str(m.hexdigest())) 
			except Exception as e: 
				print("send verification email error (login) : "+ str(e) + " " + str(date.now()) )
			
			return render_to_response('send_verification.html', {'login': True, 'done':True , 'user': user , 'username':user.username},context_instance=RequestContext(request))

	else:
		
		if request.method == "GET":
			return render_to_response('send_verification.html', context_instance=RequestContext(request))
		
		if request.method == "POST":
			
			ail = request.POST.get('ail')
			
			try:
				user = User.objects.get(email = ail)
			except:
				return render_to_response('send_verification.html', {'login': False , 'done2':True },context_instance=RequestContext(request))
			
			import hashlib
			m=hashlib.md5()
			m.update(str(user.username) + str(user.id) + str(user.email) )
			try:
				mail(userId=user.id,kind="verify",text=str(m.hexdigest())) 
			except Exception as e: 
				print("send verification email error (logout) : "+ str(e) + " " + str(date.now()) )
				
			return render_to_response('send_verification.html', {'login': False , 'done':True },context_instance=RequestContext(request))
			
	
	
@login_required
def editDescription(request):
	userprofile=UserProfile.objects.get(user=request.user)
	form={}
	form['desc'] = userprofile.text	

	if request.method == "GET":
		return render_to_response('edit-description.html', {'form':form}, context_instance=RequestContext(request))

	if request.method == "POST":
		userprofile.text=request.POST.get('desc')
		userprofile.save()

		contactFilter(userprofile.text,"edit description ,userProfile",userprofile.id)

		return HttpResponseRedirect('/profile/')

@login_required
def editEducation(request):
	userprofile=UserProfile.objects.get(user=request.user)
	form={}
	

	if request.method == "GET":

		licences=Licence.objects.all()		
		
		checked2=[]
		if userprofile.education:
			licence=userprofile.education.licence
			try:
				checked2.append(licence.name)
			except:
				pass

		education=userprofile.education
		if education:
			try:
				form['start']=education.startDate.year
			except:
				form['start']=''

			try:
				form['end']=education.endDate.year
			except:
				form['end']=''

			if education.school:
				form['school']=education.school
			else:
				form['school']=''
		return render_to_response('edit-education.html', {'form':form, 'checked2':checked2 , 'licences':licences }, context_instance=RequestContext(request))

	if request.method == "POST":

		start=end=term=school=''


		education=userprofile.education

		if education:
			education=Education.objects.get(id=userprofile.education.id)
		else:
			education=Education()

		flag=False
		
		
		if request.POST.get('licence'):
			flag=True
			licence=request.POST.get('licence')
			try:
				education.licence=Licence.objects.get(name=licence)
			except:
				pass


		if request.POST.get('start'):
			flag=True
			start=request.POST.get('start')+"-1-1"
			try:
				start = datetime.datetime.strptime(start, "%Y-%m-%d")
			except:
				return render_to_response('alert.html', {'error':"لطفا فیلد سال را به صورت ۱۳ٓٓ۰۰ وارد کنید",'address':'-1'})
			education.startDate=start


		if request.POST.get('end'):
			flag=True
			end=request.POST.get('end')+"-1-1"
			try:
				end = datetime.datetime.strptime(end, "%Y-%m-%d")
			except:
				return render_to_response('alert.html', {'error':"لطفا فیلد سال را به صورت ۱۳ٓٓ۰۰ وارد کنید",'address':'-1'})
			education.endDate=end


		if request.POST.get('school'):
			flag=True
			school=request.POST.get('school')
			education.school=school


		if(flag):
			education.save()
			userprofile.education=education
			userprofile.save()


		return HttpResponseRedirect("/profile/")


@login_required
#@csrf_response_exempt 
@csrf_exempt
def editPicture(request):
	form={}
	userprofile = UserProfile.objects.get(user=request.user)
	dest="static/files/tmpProfile/"+str(userprofile.id)+".jpg"
	form['id']=userprofile.id
	if request.method == "GET":
		return render_to_response('edit-picture.html', {'form':form,'login':True,'user':userprofile.user}, context_instance=RequestContext(request))

	if request.method == "POST":
		if request.FILES:
			f=request.FILES['f']

			if f.size > 4*1024*1024:
				string="<script type='text/javascript '> window.alert ('Image file too large ( > 4mb )' );window.location.href= '/controlPanel/';</script>"
				return HttpResponse(string)

			
			'''
			with open(dest, 'wb+') as destination:
				for chunk in f.chunks():
					destination.write(chunk)
			'''
			try:

				image = Image.open(f)

				width , height   = image.size
		
				image = image.resize( (500 , (height * 500) / width ) )
			
				image.save(dest)
			except:
				return render_to_response('alert.html', {'error':"فرمت فایل ورودی پشتیبانی نمیشود",'address':'/edit-picture/'})


			return HttpResponse(userprofile.id)

		else:
			
			
			try:
				im = Image.open(dest)
				#request.POST.get('x1'), request.POST.get('y1'), request.POST.get('width'), request.POST.get('height')
				x1 = int (request.POST.get('x1'))
				y1 = int (request.POST.get('y1'))
				x2 = int (request.POST.get('x2'))
				y2 = int (request.POST.get('y2'))
				#width = int ( request.POST.get('width') )
				#height = int ( request.POST.get('height') )

				userprofile.is_image_uploaded=True
				userprofile.save()
				#im.crop((x1,y1,x2,y2)).save("static/files/tmpProfile/result.jpg")
				dest = "static/files/profile/"+str(userprofile.id)+".jpg"
				im.crop((x1,y1,x2,y2)).save(dest)

				
				myfile="static/files/tmpProfile/"+str(userprofile.id)+".jpg"
				if os.path.isfile(myfile):
					os.remove(myfile)
				else:
					print("edit picture not found tmp profile id= "+ str(userprofile.id) + " " + str(date.now()) )


			except Exception as e: 
				print("edit picture error : "+ str(e) + " " + str(date.now()) )

			
			return HttpResponse('done')


def loginAjax(request):

	if request.method == 'POST':

		form = LoginForm(request.POST)
		if form.is_valid():
			username = request.POST.get('username', '')
			password = request.POST.get('password', '')
			
			if '@' in username :
				try:
					username = User.objects.get(email = username).username
				except:
					form.errors="لطفا ابتدا وارد لینک فعال سازی که به ایمیلتان فرستاده شده است , شوید"
					return render_to_response('loginAjax.html', {'form':form},context_instance=RequestContext(request))
				
				
			user = auth.authenticate(username=username, password=password)
			
			if user is not None and user.is_active:
				
				if user.userprofile.is_email_verified:

					if user.userprofile.is_ban :
						form.errors="کاربر گرامی اکانت کاربری شما به دلیل نقض قوانین سایت مسدود شده است. در صورت تمایل میتوانید از طریق فرم تماس با ما با عوامل سایت در تماس باشید."
						return render_to_response('loginAjax.html', {'form':form},context_instance=RequestContext(request))	
						
					auth.login(request, user)
					if redirect==0:
						return HttpResponseRedirect("/controlPanel/")
					else:
						return HttpResponseRedirect("/"+redirect+"/")
				else:
					form.errors="لطفا ابتدا وارد لینک فعال سازی که به ایمیلتان فرستاده شده است , شوید"
					return render_to_response('loginAjax.html', {'form':form},context_instance=RequestContext(request))

			else:
				form.errors="نام کاربری یا رمز عبور اشتباه است"
				return render_to_response('loginAjax.html', {'form':form},context_instance=RequestContext(request))
		else:
			return render_to_response('loginAjax.html', {'form':form},context_instance=RequestContext(request))

	elif request.method == 'GET':
		form = LoginForm()
		return render_to_response('loginAjax.html', {'form':form},context_instance=RequestContext(request))
	else:
		form = LoginForm(request.POST)
		return render_to_response('loginAjax.html', {'form':form},context_instance=RequestContext(request))


@login_required
def file(request):
	form={}
	if request.method=="POST":
		pass
	elif request.method=="GET":
		return render_to_response('file.html', {'form':form},context_instance=RequestContext(request))		
		
		
		
		
		
		
		
		
		
		
@login_required
def setting(request):

	form={'login': True,'user':request.user }
	userprofile=UserProfile.objects.get(id=request.user.id)

	if request.method=='POST':
		if request.POST.get('email'):

			try:
				user2 = UserProfile.objects.get(email=request.POST.get('email'))
				if not user2 ==userprofile:
					return render_to_response('alert.html', {'error':" این ایمیل قبلا استفاده شده است ",'address':'/setting/'},
					content_type='text/html; charset=utf-8')
			except:
				userprofile.email=request.POST.get('email')
				userprofile.save()

		if request.POST.get('current'):

			current=request.POST.get('current')

			user = authenticate(username=userprofile.user.username, password=current)

			if (not request.POST.get('new') or  not request.POST.get('confirm') or  request.POST.get('new')=='' or request.POST.get('confirm')==''):
				return render_to_response('alert.html', {'error':"پسورد ها درست وارد نشده اند",'address':'/setting/'},
					content_type='text/html; charset=utf-8')

			new = request.POST.get('new')
			confirm=request.POST.get('confirm')

			if new != confirm:
				return render_to_response('alert.html', {'error':"پسورد ها درست وارد نشده اند",'address':'/setting/'},
					content_type='text/html; charset=utf-8')

			if user is not None:
				if user.is_active:
					userprofile.user.set_password(new)
					userprofile.user.save()
					userprofile.save()

				else:
					return render_to_response('alert.html', {'error':"این اکانت مسدود شده است",'address':'0'},
						content_type='text/html; charset=utf-8')

			else:
				return render_to_response('alert.html', {'error':"پسورد وارد شده اشتباه میباشد",'address':'0'},
						content_type='text/html; charset=utf-8')


		if request.POST.get('is_subscribeForProjects'):
			userprofile.is_subscribeForProjects = True
		else:
			userprofile.is_subscribeForProjects = False
			
		if request.POST.get('is_subscribeForNotif'):
			userprofile.is_subscribeForNotif = True
		else:
			userprofile.is_subscribeForNotif = False

		userprofile.save()
		return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':'/setting/'},
						content_type='text/html; charset=utf-8')

	if request.method=='GET':
		form['email']=userprofile.user.email
		form['is_subscribeForProjects'] = userprofile.is_subscribeForProjects
		form['is_subscribeForNotif'] = userprofile.is_subscribeForNotif
		
		return render_to_response('setting.html', {'form':form,'login':True },context_instance=RequestContext(request))\
		
def handler500(request):
	return render_to_response('alert.html', {'error':"فرم به درستی تکمیل نشده است",'address':'/'},content_type='text/html; charset=utf-8')