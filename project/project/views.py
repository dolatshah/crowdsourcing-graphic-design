#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#encoding:UTF-8
import os, sys



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
from freeDesigner.forms import RegisterForm,LoginForm

from project.forms import NewProjectForm,uploadForm,MortgageForm,IncreaseTimeForm
from project.models import Project,Offering,Employee,ProjectFile,Discussion
from project.models import File as Files
from freeDesigner.models import UserProfile,Account,AccountActivity,Message,relatedProjects,projectsForOffer,Notification

#from freeDesigner.models import RankForEmployer as projefaRankForEmployer
#from freeDesigner.models import RankForEmployee as projefaRankForEmployee

from django.contrib import auth  
from django.db import connection, models
from django.core.files import File 
from django.db.models import get_app, get_models
from django.utils.timezone import utc
from django.db.models import Q
import others
import MySQLdb

import datetime





@login_required   
def newProject(request):
	try:
		userprofile=UserProfile.objects.get(id=request.user.id)
	except:
		return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/new-project/'})
	
	form = NewProjectForm()
	  
	form.login= True
	form.user=request.user 
	account=userprofile.account
	
#	form.skills = Skill.objects.all()
	
	categories={}


#	for skill in Skill.objects.all():
#		if skill.category in categories:
#			categories[skill.category].append(skill)
#		else:
#			categories[skill.category]=[skill]

	form.categories= categories

#	skills=Skill.objects.all()

	form.start = 0
	form.end = 21000000
		
	
	
	if request.method == 'POST': 


		form = NewProjectForm(request.POST)         


		if form.is_valid(): 
			
			cd = form.cleaned_data
			
			string = request.POST.get('offerValue')    
			start = 0
			end = int(string)
			
			string = request.POST.get('slider')
			startSlider = 0
			endSlider = 101
		

			hourTimeForOffer=cd['hourTimeForOffer']
			dayTimeForOffer=cd['dayTimeForOffer']
			#is_public=cd['is_public']
			

			userprofile.mobile=request.POST.get('tel')
			userprofile.save()

			


			hourTimeForOffer=hourTimeForOffer+dayTimeForOffer*24
			project=Project(employer_id=request.user.id,title=cd['title'],description=cd['description'],startBid=start,endBid=end,
						offerTime=datetime.datetime.now().replace(tzinfo=utc),is_active=1,employer_cashed_money=0,hourTimeForOffer=hourTimeForOffer,offerDay=cd['offerDay'],
						startSlider=startSlider,endSlider=endSlider,is_wait_for_employee=False,is_wait_for_employer=False,category=request.POST.get('category'),
						)
			
			if request.POST.get('is_public') == '1':
				project.is_public=True
			else:
				project.is_public=False
			
			project.save()
			

			if request.POST.get('typed-skills') and not request.POST.get('typed-skills')=='':
				typed_skills = request.POST.get('typed-skills')
				typed=typed_skills.split(',')      
				
				for skill in typed:
					if not skill=="" and not skill==" ":
						for sk in Skill.objects.all():
							if ( sk.name.strip() in skill.strip() ) and ( skill.strip() in sk.name.strip() ) :
								project.skill.add(sk) 
				project.save()

					
			if request.POST.get('licence'):
				
				licence=request.POST.get('licence')
				
				try:
					licence=Licence.objects.get(name=licence)
					project.licence.add(licence)
				except:
					pass
			

			project.save()

			
			
			try:
				for index,projectFile in enumerate( ProjectFile.objects.filter(project_id=1).order_by('uploadTime').reverse() ):
					
					if index==0:

						projectFile.project=project
						projectFile.save()
			
					else:
						
						dest="static/files/project/"+str(projectFile.id)+".zip"
						if os.path.isfile(dest):
							os.remove(dest)
						else:
							print("project file not found projectFile id = "+ str(projectFile.id) + " " + str(datetime.datetime.now().replace(tzinfo=utc) ))
						projectFile.delete()
					
			except Exception as e:
				print("new project file error : "+ str(e) + " " + str(datetime.datetime.now().replace(tzinfo=utc) ))

			
			
			related=relatedProjects(is_crowd=False,project_id=project.id,is_employer=True)
			related.save()
			userprofile.relatedProjects.add(related)
			userprofile.save()
			
			string="/project/"+str(project.id)
			#string="<script type='text/javascript '> window.alert ('با موفقیت انجام شد' );window.location.href= '/project/"+str(project.id)+"';</script>"
			

			return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})
			#return HttpResponse(string)
		
		else:
			print form.errors
			form.login= True
			
			form.user=request.user 
			account=userprofile.account
			
			
			
			form.start = 0
			form.end = 21000000

			form.titleValue=request.POST.get('title')
			form.offerDayValue=request.POST.get('offerDay')
			form.offerValueValue=request.POST.get('offerValue')
			form.telValue=request.POST.get('tel')
			form.descriptionValue=request.POST.get('description')
			form.dayTimeForOfferValue=request.POST.get('dayTimeForOffer')
			form.hourTimeForOfferValue=request.POST.get('hourTimeForOffer')




			
			
			
			return render_to_response('newproject.html', {'login':True , 'form': form},context_instance=RequestContext(request))
			
	else: 
		form.startSliderValue=1
		form.endSliderValue=101
		

		return render_to_response('newproject.html', {'form': form},context_instance=RequestContext(request))
	
		
	
	
	

def project(request,projectid,tabId=0):

	try:
		project=Project.objects.get(id=projectid)
	except:
		return render_to_response('alert.html', {'error':"اين پروژه وجود ندارد",'address':'/profile/'})
		
	if project.is_canceled or project.is_finished or project.is_failed:

		try:
			userprofile=UserProfile.objects.get(id=request.user.id)
			form={'login':True,'user':request.user,'project':project}
		except:
			form={'login':False,'user':request.user,'project':project}

		form['offerlist']=Offering.objects.filter(project=project)

		return render_to_response("doneProject.html", {'form': form,'discussions':Discussion.objects.filter(project=project)},context_instance=RequestContext(request))

	try:
		userprofile=UserProfile.objects.get(id=request.user.id)
	except:
		return others.projectForOther(request,projectid,{'login':False,'user':request.user,'project':project})
	
	

	
	employer=User.objects.get(id=project.employer_id) 
	offerlist=Offering.objects.filter(project=project) 
	account=userprofile.account
	
	sender=project.employer
	if (project.employee):
		receiver=project.employee.userprofile
		
		messages=Message.objects.filter(Q(sender=sender,receiver=receiver) | Q(sender=receiver,receiver=sender)).order_by('sentTime')

		if messages.all().count():
			lastMessageId=messages[0].id
		else:
			lastMessageId=-1
	else:    
		lastMessageId=-1

	form={'login':True,'user':request.user ,'done':False,'employer':employer,'project':project,'lastMessageId':lastMessageId
		}

	if tabId!=0:
		form['tabId']=tabId

	try:
		sue=Sue.objects.get(project=project)
		form['sue']=sue
	except:
		pass

		
	
		
	if not account.is_verified:
		form['account']="notactive"
	else:
		form['account']="active"
			
	form['account']="active"


	if project.is_running:
		form['is_running']=True
		seconds=project.endDate-datetime.datetime.now().replace(tzinfo=utc)#.replace(tzinfo=utc)
		seconds=seconds.total_seconds()
		
		form['seconds_remain']=seconds

		timediff = str(datetime.timedelta(seconds=seconds))
							
		form['time_remain']=timediff[:timediff.find('.')]
							
		if (seconds>0):
			form['is_time_remain']=True
		else:
			form['is_time_remain']=False

	else:
		form['is_running']=False

	

	if request.user.id==project.employer_id:   
		return others.projectForEmployer(request,projectid,form)         

	else:
		return others.projectForOther(request,projectid,form)                     
							
		
				
		
		
	
	   


	
import simplejson
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt    
def upload (request,projectid):


	userprofile=UserProfile.objects.get(id=request.user.id)
	try:
		project=Project.objects.get(id=projectid)
	except:
		return render_to_response('alert.html', {'error':"این پروژه وجود ندارد",'address':'/profile/'})
		



	#employee=project.employee
	
	if project.employee:
		if project.employee.userprofile!=userprofile and project.employer!=userprofile:
			#string="<script type='text/javascript '> window.alert ('شما کارفرما یا پیمانکار این پروژه نمیباشید' );history.go(-1);</script>"
			#return HttpResponse(string)
			return render_to_response('alert.html', {'error':"شما کارفرما یا پیمانکار این پروژه نیستید",'address':'-1'})
	else:
		#string="<script type='text/javascript '> window.alert ('این پروژه پیمانکار ندارد ' );history.go(-1);</script>"
		#return HttpResponse(string)
		return render_to_response('alert.html', {'error':"این پروژه پیمانکار ندارد",'address':'-1'})

	
		
	if request.method == 'POST':
		
		
		
		f=request.FILES['f']
			
		myfile=Files(uploader=userprofile,description=request.POST.get('description'),uploadTime=datetime.datetime.now().replace(tzinfo=utc),path="static/files/")
		myfile.save()

		contactFilter(myfile.description,"upload project file",myfile.id)

		dest="static/files/"+str(myfile.id)+".zip"


		project.files.add(myfile)
		project.save()
			
		with open(dest, 'wb+') as destination:
			for chunk in f.chunks():
				destination.write(chunk)
					
			
		string="/project/"+str(project.id)
		return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})
		
		
			
	
	if request.method == 'GET':

		form = uploadForm()
		form.project =project
		return render_to_response("upload.html", {'form': form,'login':True,'userprofile':userprofile,'projectid':projectid},context_instance=RequestContext(request))
	
		
	
		
	
	
	
@login_required    
def rank (request,projectid):

	userprofile=UserProfile.objects.get(id=request.user.id)
	project=Project.objects.get(id=projectid)
	
	
	casesforemployee=[]
	casesforemployer=[]

	app = get_app('project')

	for model in get_models(app):
		if model._meta.db_table=="project_rankforemployee":
			for name in model._meta.get_all_field_names():
				if name !="id" and name!="project" and name!="totalRank" and name!="employee" and name!="count":
					casesforemployee.append(name)
				
				
		if model._meta.db_table=="project_rankforemployer":
			for name in model._meta.get_all_field_names():
				if name !="id" and name!="project" and name!="totalRank" and name!="employee" and name!="count" :
					casesforemployer.append(name)
		
	if project.employee:
		if project.employee.userprofile!=userprofile and project.employer!=userprofile:
			return render_to_response('alert.html', {'error':"شما کارفرما یا پیمانکار این پروژه نیستید",'address':'-1'})
			
			#string="<script type='text/javascript '> window.alert ('you are not either employee or employer ' );history.go(-1);</script>"
			#return HttpResponse(string)
	else:
		return render_to_response('alert.html', {'error':"این پروژه پیمانکار ندارد",'address':'-1'})
	
	if request.method == 'POST':
		

		if userprofile==project.employee.userprofile:

			# text
			project.employee.rankTextForEmployer = request.POST.get('rankText')
			project.employee.save()
			project.save()
			# text

			rankForEmployer=project.employee.rankForEmployer
			flag=True

			if not rankForEmployer:
				flag=False
				rankForEmployer=RankForEmployer(totalRank=0,clarity=0,paceInPay=0,connectivity=0,tact = 0,willing =0,count=0)
			
			oldvalues = {}

			for name,key in rankForEmployer:
				if name !="id" and name!="project"  and name!="employee" and name!="count":
					oldvalues[name]=key

			s=0
			for post in request.POST:
				if post!="csrfmiddlewaretoken" and post!='rankText':
					s+=int ( request.POST.get(post) )
					setattr(rankForEmployer,post, request.POST.get(post))
			
			

			rankForEmployer.totalRank=s;

			if not project.employee.rankForEmployer:
				rankForEmployer.save()
				project.employee.rankForEmployer=rankForEmployer

			else:
				project.employee.rankForEmployer.save()            

			
			
			project.employee.save()
			project.save()

			userprofile = project.employer

			if not userprofile.rankForEmployer:
				rankForEmployer=projefaRankForEmployer(totalRank=0,clarity=0,paceInPay=0,connectivity=0,tact = 0,willing =0,count=0)
				rankForEmployer.save()
				userprofile.rankForEmployer=rankForEmployer
				userprofile.save()

			rankForEmployer=userprofile.rankForEmployer

			count = rankForEmployer.count

			point = 0
			zarib = 15

			if flag:
				for item,key in rankForEmployer:
					if item !="id" and item!="count" and item!="userprofile":
						oldvalue = oldvalues[item]
						if item == "totalRank":
							newvalue = s
						else:
							newvalue = request.POST.get(item)
							point = point + zarib * ( int (newvalue) - int(oldvalue) )
							#print point

						if count:
							insert = ( (  ( int(key) * int (count) ) - int (oldvalue) ) + int(newvalue) ) / int(count)
							setattr(rankForEmployer,item,insert)

							#print 1,item,insert
						else:
							setattr(rankForEmployer,item,newvalue)
							#print 2,item,newvalue




			else:
				count+=1
				for item,key in rankForEmployer:
					if item !="id" and item!="count" and item!="userprofile":

						oldvalue = oldvalues[item]

						if item == "totalRank":
							newvalue = s
						else:
							newvalue = request.POST.get(item)
							point = point + zarib * ( int (newvalue) - int(oldvalue) )
							#print point

						insert =  (  ( int(key) * int (count) ) + int (newvalue) ) / int(count)
						setattr(rankForEmployer,item,insert)
						#print 3,item,insert

				rankForEmployer.count=count

			rankForEmployer.save()
			userprofile.save()

			rankList = employerRankList.objects.get(userprofile=userprofile)
			rankList.point = point + rankList.point
			rankList.save()



			string="/project/"+str(project.id)
			return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})
					
			
		elif userprofile==project.employer:

			# text
			project.employee.rankTextForEmployee = request.POST.get('rankText')
			project.employee.save()
			project.save()
			# text
			
			rankForEmployee=project.employee.rankForEmployee

			flag=True
			if not rankForEmployee:
				flag=False
				rankForEmployee=RankForEmployee(totalRank=0,quality=0,pace=0,connectivity=0,tact = 0,willing =0,count = 0)





			oldvalues = {}
			for name,key in rankForEmployee:
				if name !="id" and name!="project"  and name!="employer"  and name!="employee" and name!="count" :
					oldvalues[name]=key

			s=0 
			for post in request.POST:
				if post!="csrfmiddlewaretoken" and post!='rankText':
					try:
						s+=int ( request.POST.get(post) )
						setattr(rankForEmployee,post, request.POST.get(post))
					except:
						s+=0
						setattr(rankForEmployee,post, 0)

			
				 
			rankForEmployee.totalRank=s;
			
			
			if not project.employee.rankForEmployee:
				rankForEmployee.save()
				project.employee.rankForEmployee=rankForEmployee

			else:
				project.employee.rankForEmployee.save()            
			project.employee.save()
			project.save()

			userprofile = project.employee.userprofile

			if not userprofile.rankForEmployee:
				rankForEmployee=projefaRankForEmployee(totalRank=0,quality=0,pace=0,connectivity=0,tact = 0,willing =0,count = 0)
				rankForEmployee.save()
				userprofile.rankForEmployee=rankForEmployee
				userprofile.save()

			rankForEmployee=userprofile.rankForEmployee

			count = rankForEmployee.count

			point = 0
			zarib = 15

			if flag:

				for item,key in rankForEmployee:
					if item !="id" and item!="count" and item!="userprofile":
						oldvalue = oldvalues[item]
						if item == "totalRank":
							newvalue = s
						else:

							newvalue = request.POST.get(item)
							point = point + zarib * ( int (newvalue) - int(oldvalue) )
							#print point

						if count:
							insert = ( (  ( int(key) * int (count) ) - int (oldvalue) ) + int(newvalue) ) / int(count)
							setattr(rankForEmployee,item,insert)

							#print 1,item,insert
						else:
							setattr(rankForEmployee,item,newvalue)
							#print 2,item,newvalue




			else:

				count+=1
				for item,key in rankForEmployee:
					if item !="id" and item!="count" and item!="userprofile":

						oldvalue = oldvalues[item]

						if item == "totalRank":
							newvalue = s
						else:
							newvalue = request.POST.get(item)
							point = point + zarib * ( int (newvalue) - int(oldvalue) )
							#print point

						insert =  (  ( int(key) * int (count) ) + int (newvalue) ) / int(count)
						setattr(rankForEmployee,item,insert)
						#print 3,item,insert

				rankForEmployee.count=count

			rankForEmployee.save()
			userprofile.save()

			rankList = employeeRankList.objects.get(userprofile=userprofile)
			rankList.point = point + rankList.point
			rankList.save()
			string="/project/"+str(project.id)
			return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})
			
		
		else:
			string="/project/"+str(project.id)
			return render_to_response('alert.html', {'error':"شما اجازه ی رتبه دهی به این پروژه را ندارید",'address':string})
			
	
	if request.method == 'GET':
		
		valueCases={}
		if userprofile==project.employee.userprofile:
			
			form={'cases':casesforemployer,'is_employer':False}

			if project.employee.rankForEmployer:
				for name, val in project.employee.rankForEmployer:
					if name !="id" and name!="project" and name!="totalRank" and name!="employee" and name!="count":
						valueCases[name]=val

			form['project']=project
			form['valueCases']=valueCases
			form['rankText']=project.employee.rankTextForEmployer

			return render_to_response("RankModal.html", {'form': form,'login':True,'userprofile':userprofile},context_instance=RequestContext(request))

		elif userprofile==project.employer:
			form={'cases':casesforemployee,'is_employer':True}

			if project.employee.rankForEmployee:
				for name, val in project.employee.rankForEmployee:
					if name !="id" and name!="project" and name!="totalRank" and name!="employer" and name!="count":
						valueCases[name]=val
			
			form['valueCases']=valueCases
			form['project']=project
			form['rankText']=project.employee.rankTextForEmployee
			return render_to_response("RankModal.html", {'form': form,'login':True,'userprofile':userprofile},context_instance=RequestContext(request))

		else:

			string="/project/"+str(project.id)
			return render_to_response('alert.html', {'error':"شما اجازه ی رتبه دهی به این پروژه را ندارید",'address':string})
	
		
		
			
			
	 
	 
@login_required
def done (request,projectid):

	
	#admin=UserProfile.objects.get(is_admin=1)
	userprofile=UserProfile.objects.get(id=request.user.id)
	project=Project.objects.get(id=projectid)


	

	employer=project.employer
	
	if project.is_finished :
		return render_to_response('alert.html', {'error':"پروژه با موفقیب به پایان رسیده است",'address':'/profile/'})

	if userprofile!=employer:
		return render_to_response('alert.html', {'error':"شما اجازه دسترسی به این صفحه را ندارید",'address':'/profile/'})
	
	
	
	if request.method == 'GET':
		#if not project.employee.rankForEmployee or project.employee.rankForEmployee==None:
		#	string="/project/"+str(project.id)
		#	return render_to_response('alert.html', {'error':"شما هنوز به پیمانکار خود امتیاز نداده اید",'address':string})

		if  5*int(project.employer_cashed_money)/100 > 5000:
			comission=5*int(project.employer_cashed_money)/100
		else:
			comission=5000



		project.employee.userprofile.account.money=str (  int (project.employee.userprofile.account.money) + int (project.employer_cashed_money) + int (project.employee.cashedMoney) - int(comission) )
		project.employee.gainedMoney= str ( int (project.employer_cashed_money)  - int(comission) )


		activity=AccountActivity(activityType="C",
				transmitedMoney=str ( int (project.employer_cashed_money) + int (project.employee.cashedMoney) - int(comission) ),
				transferTime=datetime.datetime.now().replace(tzinfo=utc),
				description="کمیسیون و بیعانه ی کارفرما و ضمانت شما")

		activity.save()
		project.employee.userprofile.account.accountActivity.add(activity)
		project.employee.userprofile.account.save()
		project.employee.userprofile.save()
		project.employee.save()
		
		
		message=Notification(sender="admin",receiver=project.employer,text=u'تبریک! پروژه با موفقیت انجام شد',sentTime=datetime.datetime.now().replace(tzinfo=utc),is_read=False)
		message.save()
		
		message=Notification(sender="admin",receiver=project.employer,text=u"کمیسیون سایت از مبلغ معاوضه شد کاسته شد",sentTime=datetime.datetime.now().replace(tzinfo=utc),is_read=False)
		message.save()

		message=Notification(is_read=False,sender="admin",receiver=project.employee.userprofile,text=u'تبریک پروژه با موفقیت انجام شد',sentTime=datetime.datetime.now().replace(tzinfo=utc))
		message.save()
		
		message=Notification(sender="admin",receiver=project.employee.userprofile,text=u"کمیسیون سایت از مبلغ معاوضه شد کاسته شد",sentTime=datetime.datetime.now().replace(tzinfo=utc),is_read=False)
		message.save()

		project.is_finished=True
		project.is_running=False
		project.is_active=False
		project.is_failed=False


		project.save()
		
		#mail(userId=1,kind="contact",text='done Project.id=' + str(projectid) + " employer cashedMoney= " + str(project.employer_cashed_money) )

		string="/project/"+str(project.id)
		return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})
			

	
	
@login_required
def cancel(request,projectid):
	
	#admin=UserProfile.objects.get(is_admin=1)
	userprofile=UserProfile.objects.get(id=request.user.id)
	project=Project.objects.get(id=projectid)
	employer=project.employer
	employee=project.employee

	
	if project.is_canceled:
		return render_to_response('alert.html', {'error':"پروژه بسته شده است",'address':'/profile/'})
	
	#mail(userId=1,kind="contact",text='cancel Project.id='+str(projectid))
	
	if userprofile==employer:

		if project.is_running == False :# hanooz shoro nashode
			
			employer.account.money = str( int (employer.account.money) + int (project.employer_cashed_money) )
			activity=AccountActivity(activityType="C",
				transmitedMoney=str( project.employer_cashed_money) ,
				transferTime=datetime.datetime.now().replace(tzinfo=utc),
				description="بیعانه پروژه لغو شده")

			activity.save()
			employer.account.accountActivity.add(activity)
			employer.account.save()
			employer.save()

		else: # shoro shode

			if int(project.employer_cashed_money)*5/100>5000:
				jarime=int(project.employer_cashed_money)*5/100
			else:   
				jarime=5000

			employee.userprofile.account.money=str( int (employee.userprofile.account.money) + int (project.employer_cashed_money) + int (employee.cashedMoney) - int (jarime) )
			employee.gainedMoney= str ( int (project.employer_cashed_money)  - int(jarime) )

			activity=AccountActivity(activityType="C",
				transmitedMoney=str ( int (project.employer_cashed_money) + int (employee.cashedMoney) - int(jarime) ),
				transferTime=datetime.datetime.now().replace(tzinfo=utc),
				description="ضمانت کارفرما و بیعانه شما")

			
			activity.save()
			employee.userprofile.account.accountActivity.add(activity)
			employee.userprofile.account.save()
			employee.userprofile.save()
			employee.cashedMoney=0
			employee.save()

			
			message=Notification(is_read=False, sender="admin",receiver=employee.userprofile,text=u"پروژه توسط کارفرما بسته شد",sentTime=datetime.datetime.now().replace(tzinfo=utc))
			message.save()


		message=Notification(is_read=False, sender="admin",receiver=employer,text=u"پروژه توسط شما بسته شد",sentTime=datetime.datetime.now().replace(tzinfo=utc))
		message.save()

		project.choosedOffer_id=None
		#project.employer_cashed_money=0

		project.is_wait_for_employee=False
		project.is_wait_for_employer=False

		project.is_finished=False
		project.is_running=False
		project.is_active=False
		project.is_canceled=True
		project.is_failed=True        
		

		project.save()

			
			
			
	elif userprofile==employee.userprofile:

		if int(project.endBid)*5/100>10000:
			jarime=int(project.endBid)*5/100
		else:   
			jarime=10000

		employee.userprofile.account.money=str( int (employee.userprofile.account.money) - int (jarime) )

		activity=AccountActivity(activityType="C",
			transmitedMoney=str(jarime),
			transferTime=datetime.datetime.now().replace(tzinfo=utc),
			description="جریمه برای بستن پروژه")

		activity.save()
		employee.userprofile.account.accountActivity.add(activity)
		employee.userprofile.account.save()
		employee.userprofile.save()


		employer.account.money = str ( int (employer.account.money) + int (employee.cashedMoney) + int (project.employer_cashed_money) )
		activity=AccountActivity(activityType="C",
			transmitedMoney=str( int (employee.cashedMoney) + int (project.employer_cashed_money) ),
			transferTime=datetime.datetime.now().replace(tzinfo=utc),
			description="بیعانه کارفرما و ضمانت پیمانکار")

		activity.save()
		employer.account.accountActivity.add(activity)
		employer.account.save()
		employer.save()

		message=Message(sender=employee.userprofile,receiver=employer,text=u'من قادر به انجام پروژه نبوده و پروژه را بستم',sentTime=datetime.datetime.now().replace(tzinfo=utc))
		message.save()

		employee.gainedMoney=0
		employee.is_canceled=1
		employee.cashedMoney=0
		employee.save()

		project.choosedOffer_id=None
		#project.employer_cashed_money=0
		project.is_running=False
		project.is_active=False
		project.is_canceled=True
		project.is_failed=True        
		project.is_wait_for_employee=False
		project.is_wait_for_employer=False

		project.save()
									
									
	else:
		return render_to_response('alert.html', {'error':"شما اجازه دسترسی به این صفحه را ندارید",'address':'/profile/'})
	
	
	string="/project/"+str(project.id)
	return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})
	
		
		
	


	 
	 
	 






def mortgageincrease(request,projectid,is_offerValue):
	
	is_offerValue = int (is_offerValue)

	if request.user.is_authenticated():
		
		userprofile=UserProfile.objects.get(id=request.user.id)
		project=Project.objects.get(id=projectid)
		employees=Employee.objects.filter(project=project)
		employer=project.employer
		account=employer.account
		
		if userprofile!=employer:
			return render_to_response('alert.html', {'error':"شما اجازه دسترسی به این صفحه را ندارید",'address':'-1'})
		
		if request.method == 'POST':
			form = MortgageForm(request.POST)
			 
			if form.is_valid(): 
				cd = form.cleaned_data
				amount=cd['amount']

				if is_offerValue:
					#project.offerValue = str ( int (project.offerValue) + int (amount) )
					address="/project/"+projectid
					return render_to_response('alert.html', {'error':"اعمال تغییرات فقط تا قبل از شروع پروژه امکان پذیر بود",'address':address},
						content_type='text/html; charset=utf-8')

				
				else:
					if int (account.money) < int (amount):
						return render_to_response('alert.html', {'error':"حساب مالی شما دارای اعتبار کافی نیست.",'address':'/account/deposit-tab/'})
					else:
						account.money=str ( int(account.money) - int (amount) )
						account.save()

						activity=AccountActivity(activityType="W",transmitedMoney=str(amount),transferTime=datetime.datetime.now().replace(tzinfo=utc),description="بیعانه واریزی برای پروژه")
						activity.save()
						account.accountActivity.add(activity)
						account.save()

						project.employer_cashed_money= str ( int(project.employer_cashed_money)+int(amount))

						#mail(userId=1,kind='contact',text="mortgageincrease Project.id = "+ str(projectid) +" amount= " +str(amount) )

				project.save()
				string="/project/"+str(project.id)
				return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})

			else:
				string="/project/"+str(project.id)
				return render_to_response('alert.html', {'error':"خطا در اطلاعات فرم",'address':string})
				
			
		
		if request.method == 'GET':
			form=MortgageForm()
			form.is_offerValue=is_offerValue

			form.user=userprofile
			form.project=project
			
			return render_to_response("mortgage.html", {'form': form,'login':True},context_instance=RequestContext(request)) 
			
		
		
	
	else:
		return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/'})


@login_required
def timeincrease(request,projectid,is_offer):
	
	if request.user.is_authenticated():
		


		userprofile=UserProfile.objects.get(id=request.user.id)
		try:
			project=Project.objects.get(id=projectid)
		except:
			return render_to_response('alert.html', {'error':"این پروژه وجود ندارد",'address':'-1'})
		employees=Employee.objects.filter(project=project)
		employer=project.employer
		account=employer.account
		
		if userprofile!=employer:
			return render_to_response('alert.html', {'error':"شما اجازه دسترسی به این صفحه را ندارید",'address':'-1'})
			#return HttpResponse(string)
		
		if request.method == 'POST':


			form = IncreaseTimeForm(request.POST)
			 
			if form.is_valid(): 
				cd = form.cleaned_data
				day=cd['day']
				month=cd['month']
				
				if month>0:
					day=month*30+day
				
				if is_offer=='1':

					if ( datetime.datetime.now().replace(tzinfo=utc)-project.offerTime-datetime.timedelta(hours=project.hourTimeForOffer) ).total_seconds() > 0: #passed

						dateTillNow = datetime.datetime.now().replace(tzinfo=utc) - project.offerTime
						hoursTillNow = dateTillNow.total_seconds()/3600 
						project.hourTimeForOffer=int(hoursTillNow)+day+1

					else:# not  passed

						project.hourTimeForOffer=project.hourTimeForOffer+day
				else:

					if ( datetime.datetime.now().replace(tzinfo=utc)-project.endDate ).total_seconds() > 0:# passed

						project.endDate=datetime.datetime.now().replace(tzinfo=utc)+datetime.timedelta(days=day)

					else:# not passed

						project.endDate=project.endDate+datetime.timedelta(days=day)
					
					
					
				project.save()
				string="/project/"+str(project.id)	
				return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})
			
			else:
				#form=IncreaseTimeForm()
				form.login=True
				form.user=userprofile
				form.is_offer=is_offer
				return render_to_response("timeincrease.html", {'form': form},context_instance=RequestContext(request))
			
		
		if request.method == 'GET':
			form=IncreaseTimeForm()
			form.login=True
			form.user=userprofile
			form.is_offer=is_offer
			return render_to_response("timeincrease.html", {'form': form,'project':project},context_instance=RequestContext(request)) 
			
		
		
	
	else:
		return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/'})


def changeOffer(request,projectid,offerid):

	project=Project.objects.get(id=projectid)
	userprofile=UserProfile.objects.get(id=request.user.id)
	seconds=datetime.timedelta(hours=project.hourTimeForOffer)+project.offerTime-datetime.datetime.now().replace(tzinfo=utc)
	
	seconds=seconds.total_seconds()
	timediff = str(datetime.timedelta(seconds=seconds))

	return others.changeOffer(request,projectid,offerid)    

	

def deleteOffer(request,offerid):
	offer=Offering.objects.get(id=offerid)
	userprofile=UserProfile.objects.get(id=request.user.id)
	userprofile.account.money= str ( int(offer.value) +  int (userprofile.account.money) )
	userprofile.account.save()
	userprofile.save()
	Offering.objects.get(id=offerid).delete()
	return HttpResponse("done")



def acceptOffer(request,offerid):
	
	offer=Offering.objects.get(id=offerid)


	

	#admin=UserProfile.objects.get(is_admin=True)
	project=offer.project    

	

	#print("acceptOffer project.id= "+ str(project.id) + " offer.id= " + str(offer.id) + " " + str(datetime.datetime.now().replace(tzinfo=utc) ))
	


	employer=project.employer

	if project.is_wait_for_employee:
		return HttpResponse('1')

	
	#if int(employer.account.money) + int(project.employer_cashed_money) < int(offer.value):
	 #   return HttpResponse('2')



	else:
		offer.is_accepted_by_employer=True  
		offer.save()
		project.is_wait_for_employee=True


			

	project.choosedOffer_id=offer.id
	

	project.save()

	message=Notification(is_read=False, sender="admin",receiver=offer.offerer,text=u"تبریک!کارفرما شما را برای انجام پروژه انتخاب کرده است" 
		,sentTime=datetime.datetime.now().replace(tzinfo=utc))
	message.save()    

	#mail(userId=1,kind="contact",text='acceptOffer project.id='+str(project.id))    
	return render_to_response("acceptedOffer.html", {'offer': offer}) 


def cancelOffer(request,offerid):
	
	offer=Offering.objects.get(id=offerid)
	#admin=UserProfile.objects.get(is_admin=True)
	project=offer.project    

	

	#print("cancel offer project.id = "+ str(project.id) + " offer.id= " + str(offer.id) + " " + str(datetime.datetime.now().replace(tzinfo=utc) ))

	employer=project.employer

	if offer.is_accepted_by_employer == False:
		string="/project/"+str(project.id)  
		return render_to_response('alert.html', {'error':"خطایی رخ داده است لطفا با عوامل سایت درمیان بگذارید",'address':string})

	if project.is_wait_for_employee:

		offer.is_accepted_by_employer=False
		offer.save()

		#employer.account.money = str (int(employer.account.money) + int (offer.value))
		#project.employer_cashed_money = str ( int (project.employer_cashed_money ) - int (offer.value ) )


		
		#activity=AccountActivity(activityType="W",
				#transmitedMoney=offer.value,
				#transferTime=datetime.datetime.now().replace(tzinfo=utc),
				#description="بیعانه پیمانکار برای انجام پروژه")
		
		#activity.save()
		#employer.account.accountActivity.add(activity)
		#employer.account.save()    
		#employer.save()

		project.is_wait_for_employee=False
		project.choosedOffer_id=None
		project.save()

		message=Notification(is_read=False, sender="admin",receiver=offer.offerer,text=u"کارفرما پیشنهاد شما را رد کرد" ,sentTime=datetime.datetime.now().replace(tzinfo=utc))
		message.save()    
		
		#string="/project/"+str(project.id)
		#return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})
		#mail(userId=1,kind="contact",text='cancelOffer project.id='+str(project.id))
		return HttpResponse('done')
		
	else:
		return render_to_response('alert.html', {'error':"شما اجازه دسترسی به این صفحه را ندارید",'address':'-1'})

@login_required
def completeByEmployee(request,projectid):
	

	#print("complete by employee project.id = "+ str(projectid) + " " + str(datetime.datetime.now().replace(tzinfo=utc) ))
	userprofile=UserProfile.objects.get(id=request.user.id)

	project=Project.objects.get(id=projectid)

	if project.employee.userprofile!=userprofile:
		return render_to_response('alert.html', {'error':"شما اجازه دسترسی به این صفحه را ندارید",'address':'-1'})
	else:
		message=Message(sender=userprofile,receiver=project.employer,text=u'پیمانکار شما از شما درخواست انجام شده دانستن پروژه کرده است',sentTime=datetime.datetime.now().replace(tzinfo=utc))
		message.save()        
		project.is_wait_for_employer=1
		project.is_denied=False
		project.wait_for_employer_date=datetime.datetime.now().replace(tzinfo=utc)
		project.save()

	string="/project/"+str(project.id)
	return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})


@login_required
def deny(request,projectid):
	
	#print("deny project.id = "+ str(projectid) + " " + str(datetime.datetime.now().replace(tzinfo=utc) ))

	userprofile=UserProfile.objects.get(id=request.user.id)

	project=Project.objects.get(id=projectid)

	if project.employer!=userprofile:
		return render_to_response('alert.html', {'error':"شما اجازه دسترسی به این صفحه را ندارید",'address':'-1'})
	else:
		message=Message(sender=userprofile,receiver=project.employee.userprofile,text=u'به نظر من پروژه کامل نیست و باید ادامه پیدا کند',sentTime=datetime.datetime.now().replace(tzinfo=utc))
		message.save()        
		project.is_wait_for_employer=0
		project.wait_for_employer_date=None
		project.is_denied=True

		project.save()

	mail(userId=1,kind="contact",text='deny Project.id='+str(projectid))
	
	string="/project/"+str(project.id)
	return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':string})


@login_required
def editProject(request,projectid):
	
	userprofile=UserProfile.objects.get(id=request.user.id)
	project=Project.objects.get(id=projectid)

	employer=project.employer
	
	
	if userprofile!=employer:
		string="شما اجازه دسترسی به این صفحه را ندارید"
		address='/project/'+projectid
		return render_to_response('alert.html', {'error':string,'address':address},
					content_type='text/html; charset=utf-8')
	
	
	if request.method == 'POST':

		string = request.POST.get('offerValue')    
		#dash = string.find('-')

		#start = string[:dash-1]
		#end = string[dash + 2:]
		start = 0;
		end = int(string);

		project.startBid=start
		project.endBid=end
		
		
		string = request.POST.get('slider')    
		#dash = string.find('-')

		#start = string[:dash-1]
		#end = string[dash + 2:]
		start = 0;
		end = 0;

		project.startSlider=start
		project.endSlider=end

		project.description=request.POST.get('description')
		
		if not request.POST.get('offerDay'):
			string="اطلاعات وارد شده اشتباه میباشد"
			address='/editProject/'+projectid
			return render_to_response('alert.html', {'error':string,'address':address},
					content_type='text/html; charset=utf-8')

		try:
			int(request.POST.get('offerDay'))
		except:
			string="اطلاعات وارد شده اشتباه میباشد"
			address='/editProject/'+projectid
			return render_to_response('alert.html', {'error':string,'address':address},
					content_type='text/html; charset=utf-8')

		if int(request.POST.get('offerDay')) < 0:
			string="اطلاعات وارد شده اشتباه میباشد"
			address='/editProject/'+projectid
			return render_to_response('alert.html', {'error':string,'address':address},
					content_type='text/html; charset=utf-8')


		project.offerDay=request.POST.get('offerDay')

		project.save()

		#contactFilter(project.description,"project description",project.id)

		string="عملیات با موفقیت انجام شد"
		address='/project/'+str(projectid)
		return render_to_response('alert.html', {'error':string,'address':address},
					content_type='text/html; charset=utf-8')


	if request.method == 'GET':
		form={}
		form['project']=project
		form['offerDay']=project.offerDay
		form['description']=project.description

		return render_to_response('editProject.html', {'login':True,'user':userprofile.user,'form': form},context_instance=RequestContext(request))
		

@login_required
def completeOffer(request,offerid):
	
	userprofile=UserProfile.objects.get(id=request.user.id)

	try:
		offer = Offering.objects.get(id=offerid) 
	except:
		return render_to_response('alert.html', {'error':"چنین پیشنهادی وجود ندارد",'address':'0'},
					content_type='text/html; charset=utf-8')


	if not offer.project.employer.id == request.user.id:
		return render_to_response('alert.html', {'error':"شما اجازه مشاهده این صفحه را ندارید",'address':'0'},
					content_type='text/html; charset=utf-8')


	view = UserProfile.objects.get(id=offer.offerer.id)

	if request.method == 'GET':
		form={}
		form['offer']=offer

		form['employeeRank'] = employeeRankList.objects.get(userprofile=view).rank

		try:
			form['totalRank'] = view.rankForEmployee.totalRank/5
		except:
			form['totalRank'] = -1


		employerProjects=[]
		employeeProjects=[]
		projectsForOffer=[]

		import operator




		projects={}

		for related in view.projectsForOffer.all():

			project=Project.objects.get(id=related.project_id)

			if not project.is_running:
				projects[project]= datetime.timedelta(hours=project.hourTimeForOffer) + project.offerTime -datetime.datetime.now().replace(tzinfo=utc)#.replace(tzinfo=utc)

		projectsForOffer = sorted(projects.iteritems(), key=operator.itemgetter(1))[:20]





		for related in view.relatedProjects.all():
			if not related.is_crowd:
				project=Project.objects.get(id=related.project_id)
				if related.is_employer:
					if not project in employerProjects:
						employerProjects.append(project)
						continue
				else:
					if not project in employeeProjects:
						employeeProjects.append(project)
						continue


		form['employerProjects']=employerProjects
		form['employeeProjects']=employeeProjects

		#form['projectsForOffer']=projectsForOffer
		form['view']=view
		#form['description']=project.description

		return render_to_response('completeOffer.html', {'login':True ,'form': form},context_instance=RequestContext(request))

def showRank(request,projectid,is_employer):

	try:
		project=Project.objects.get(id=projectid)
	except:
		return render_to_response('alert.html', {'error':"این پروژه وجود ندارد",'address':'0'})
		return HttpResponse(string)

	form={}


	if request.method == 'GET':
		if str(is_employer)=='1':
			return render_to_response("showRank.html", {'project':project,'employee':False},context_instance=RequestContext(request))
		else:
			return render_to_response("showRank.html", {'project':project,'employee':True},context_instance=RequestContext(request))

@login_required
def removeUpload(request,fileid):
	
	userprofile=UserProfile.objects.get(id=request.user.id)

	try:
		f=Files.objects.get(id=fileid)
	except:
		return render_to_response('alert.html', {'error':"چنین فایلی وجود ندارد",'address':'-1'})

	if f.uploader == userprofile:
		f.delete()
		return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':'-1'})
	else:
		return render_to_response('alert.html', {'error':"شما اجازه انجام این عملیات را ندارید",'address':'-1'})

@csrf_exempt
def advancedSearch(request,pageNumber=1, Category=0, sk=0):
	try:
		pageNumber=int(pageNumber)
	except:
		pageNumber=1

	start=(pageNumber-1)*25
	end=pageNumber*25

	documentPerPage = 1

	form = {}

	if sk:
		form['selectedSkill']=sk;

		import MySQLdb as mdb
		con = mdb.connect(host="localhost",user="root",passwd="wasd",db="projefa",charset='utf8',use_unicode=True)
		cur = con.cursor(mdb.cursors.DictCursor)

		skillId=-1
		licenceId=-1

		for skill in Skill.objects.all():
			text=sk
			text.replace(" ", "")
			if re.match(text, skill.name, re.M | re.I):
				skillId=skill.id
				break

		for licence in Licence.objects.all():
			text=sk
			text.replace(" ", "")
			if re.match(text, licence.name, re.M | re.I):
				licenceId=licence.id
				break

		form['skilledPeople']=0

		query="""
			SELECT auth_user.username,projefa_employeeranklist.point,projefa_employeeranklist.rank 
			from auth_user,projefa_employeeranklist,projefa_userprofile
			where 
				projefa_userprofile.id = auth_user.id and 
				projefa_userprofile.id = projefa_employeeranklist.userprofile_id and 
				(
				projefa_userprofile.id in  ( SELECT userprofile_id from projefa_userprofile_skill where skill_id=%s)
				or 
				projefa_userprofile.id in (select id from projefa_education where licence_id=%s)
				)
			order by
				projefa_employeeranklist.rank
			""" % (str(skillId), str(licenceId))

		cur.execute(query)
		form['skilledPeople'] = cur.fetchall()	


		try:
			template_name = "skills-description/"+skillId+".html"
			get_template(template_name)
			form['dedicatedTemplate']="skills-description/"+skillId+".html"
		except Exception as e: 
			form['dedicatedTemplate']="skills-description/default.html"

		
	if request.POST.get('o'):
		order = request.POST.get('o')
	else:
		order = "2"

	if request.POST.get('r'):
		reverse = request.POST.get('r')
	else:
		reverse = "1"

	if request.POST.get('test'):
		form['isAdvancedSearch'] = request.POST.get('test')
	else:
		form['isAdvancedSearch'] = 0

	if Category == "last-projects" and request.method == "GET":
		order = "2"

	form['order'] = order

	if order == '1':
		order = "startBid"
	else:
		order = "offerTime"

	form['checkedStatus'] = '0'
	form['start'] = 0
	form['end'] = 500
	form['postedTime'] = '0'
	form['offerTime'] = '4'
	form['proposedTime'] = '0'

	form['reverse'] = reverse





	#if request.method=="POST":
	if 1 == 1:
		projects = []

		if request.POST.get('text'):

			text = request.POST.get('text')

			form['query'] = text

			text = r".*" + text + ".*"


			try:

				if reverse == '1':

					for project in Project.objects.all().order_by(order).reverse():
						
						if project.title and re.match(text, project.title, re.M | re.I):
							projects.append(project)
							continue

						if project.description and re.match(text, project.description, re.M | re.I):
							projects.append(project)
							continue

						for skill in project.skill.all():
							if re.match(text, skill.name, re.M | re.I):
								projects.append(project)
								continue

						for licence in project.licence.all():
							if re.match(text, licence.name, re.M | re.I):
								projects.append(project)
								continue



				else:

					for project in Project.objects.all().order_by(order):
						if project.title and re.match(text, project.title, re.M | re.I):
							projects.append(project)
							continue

						if project.description and re.match(text, project.description, re.M | re.I):
							projects.append(project)
							continue

						for skill in project.skill.all():
							if re.match(text, skill.name, re.M | re.I):
								projects.append(project)
								continue
								
						for licence in project.licence.all():
							if re.match(text, licence.name, re.M | re.I):
								projects.append(project)
								continue


			except Exception as e: 
				projects=[]


		else:
			if reverse == '1':
				projects = Project.objects.all().order_by(order).reverse()
			else:
				projects = Project.objects.all().order_by(order)

		formSkillList = []

		if request.POST.get("skillList") or Category == "my-skill" or Category == "skill":


			skillList = ""

			if request.POST.get("skillList"):
				skillList = request.POST.get("skillList")
				skills = skillList.split(',')

			elif Category == "my-skill":

				form['tabId']="my-skill"

				try:
					userprofile = UserProfile.objects.get(id=request.user.id)
				except:
					#string = "<script type='text/javascript '> window.alert ('please login');window.location.href= '/login/';</script>"
					#return HttpResponse(string)
					return render_to_response('alert.html', {'error':"ابتدا وارد شوید",'address':'/login/'})

				skills = userprofile.skill.all()

			else:
				skills = [sk]

			projects1 = []

			if skillList != "" or skills:
				for project in projects:
					for skill in project.skill.all():
						for text in skills:
							try:
								text = text.name
							except:
								pass
							try:
								text.replace(" ", "")
							except:
								text=str(text)
								text.replace(" ", "")
							if text not in formSkillList:
								formSkillList.append(text)
							if re.match(text, skill.name, re.M | re.I):
								projects1.append(project)
								break

				projects = projects1
				projects1 = []



		form['formSkillList'] = formSkillList

		projects1 = []
		if request.POST.get('postedTime') and request.POST.get('postedTime') != '0':
			form['postedTime'] = request.POST.get('postedTime')
			for project in projects:
				t = int(request.POST.get('postedTime'))
				#.replace(tzinfo=utc)
				different = date.now() - project.offerTime
				seconds = different.total_seconds()

				if t == 1:
					if seconds < 1 * 60 * 60:
						projects1.append(project)
						continue
				if t == 2:
					if seconds < 24 * 60 * 60:
						projects1.append(project)
						continue
				if t == 3:
					if seconds < 7 * 24 * 60 * 60:
						projects1.append(project)
						continue

				if t == 4:
					if seconds < 30 * 24 * 60 * 60:
						projects1.append(project)
						continue
				if t == 5:
					if seconds < 365 * 24 * 60 * 60:
						projects1.append(project)
						continue
			projects = projects1
			projects1 = []



		projects1 = []
		if request.POST.get('offerTime') and request.POST.get('offerTime') != '4':
			form['offerTime'] = request.POST.get('offerTime')
			for project in projects:
				t = int(request.POST.get('offerTime')) + 1

				different = project.offerTime + datetime.timedelta(
					hours=project.hourTimeForOffer) - date.now()#.replace(tzinfo=utc)
				seconds = different.total_seconds()

				if t == 1:
					if seconds < 1 * 60 * 60:
						projects1.append(project)
						continue
				if t == 2:
					if seconds < 24 * 60 * 60:
						projects1.append(project)
						continue
				if t == 3:
					if seconds < 7 * 24 * 60 * 60:
						projects1.append(project)
						continue

				if t == 4:
					if seconds > 7 * 24 * 60 * 60:
						projects1.append(project)
						continue
			projects = projects1
			projects1 = []



		projects1 = []
		if request.POST.get('proposedTime') and request.POST.get('proposedTime') != '0':
			form['proposedTime'] = request.POST.get('proposedTime')

			for project in projects:
				t = int(request.POST.get('proposedTime'))

				if t == 1:
					if project.offerDay == 1:
						projects1.append(project)
						continue
				if t == 2:
					if 1 < project.offerDay and project.offerDay <= 7:
						projects1.append(project)
						continue
				if t == 3:
					if 7 < project.offerDay and project.offerDay <= 28:
						projects1.append(project)
						continue

				if t == 4:
					if project.offerDay > 30:
						projects1.append(project)
						continue
			projects = projects1
			projects1 = []



		if request.POST.get('status'):
			form['checkedStatus'] = request.POST.get('status')
			status = request.POST.get('status')

			if status == '0':
				for project in projects:
					if project.is_active:
						projects1.append(project)
						continue

			if status == '1':
				for project in projects:
					if project.is_finished:
						projects1.append(project)
						continue

			if status == '2':
				for project in projects:
					if project.is_canceled:
						projects1.append(project)
						continue

			if status == '3':
				for project in projects:
					if project.is_running:
						projects1.append(project)
						continue

			projects = projects1
			projects1 = []


		if request.POST.get('offerValue'):

			string = request.POST.get('offerValue')
			dash = string.find('-')
			try:
				start = int(string[:dash])
			except:
				start=0
			try:
				end = int(string[dash + 1:])
			except:
				end= 21000000

			form['start'] = 0
			form['end'] = 500




			for project in projects:
				try:
					if end >= int(project.startBid) or int(project.endBid) >= start :
						projects1.append(project)
						continue
				except:
					pass



			projects = projects1
			projects1 = []



		if not request.user.is_authenticated():
			tempProjects = []
			for project in projects:
				if project.is_public :
					tempProjects.append(project)

			projects = tempProjects
		
		if Category == "last-projects" :
			temp1Projects = []
			for project in projects:
				if not project.is_canceled and not project.is_canceled:
					temp1Projects.append(project)
			projects = temp1Projects

		pages = len(projects) / documentPerPage

		if pages > 5:
			form['pages'] = range(1, 6)
		else:
			form['pages'] = range(1, pages + 1)

		form['documentPerPage'] = documentPerPage
		form['projects'] = projects
		form['projectsLen'] = len(projects)
		


	if request.user.is_authenticated():

		return render_to_response('advancedSearch.html', {'login': True,'sl': "%d:%d" % (start,end),'totallPage':int(len(projects)/25)+1,'pageNumber':pageNumber,'form': form},context_instance=RequestContext(request))
	else:
		return render_to_response('advancedSearch.html', {'login': False,'sl': "%d:%d" % (start,end),'totallPage':int(len(projects)/25)+1,'pageNumber':pageNumber, 'form': form},context_instance=RequestContext(request))

@login_required
def sue(request, projectid):
	return render_to_response('alert.html', {'error':"پروژه شما در مسیر قضاوت توسط کارشناسان سایت قرار گرفت . نتیجه قضاوت تا 7 روز آینده مشخص خواهد شد . برای تسریع در پروسه رسیدگی به شکایت دلایل عدم رضایت خود از پروژه را برای ما ایمیل کنید .",'address':'-1'})

def addfile(request, offerid, file):
	offer=Offering.objects.get(id=offerid)
	offer.image = offer.image + "," + str(file)
	offer.save()
	return render_to_response('alert.html', {'error':"عکس مورد نظر با موفقیت ارسال شد.",'address':'-1'})