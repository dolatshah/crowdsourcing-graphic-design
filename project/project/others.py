#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#encoding:UTF-8
import os, sys
from math import floor
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
from project.models import Project,Offering,File,Employee,Discussion,ProjectFile
from freeDesigner.models import UserProfile,Account,AccountActivity,Message,relatedProjects,Notification
from django.contrib import auth  
import datetime
from django.utils.timezone import utc
from datetime import timedelta
import MySQLdb
from django.db import connection, models
from django.core.files import File 
from django.db.models import get_app, get_models
import views
from shutil import copyfile
from math import floor



@login_required
def projectForEmployer(request,projectid,form):

	userprofile=UserProfile.objects.get(id=request.user.id)
	#admin=UserProfile.objects.get(is_admin=1)
	project=Project.objects.get(id=projectid)
	offerlist=Offering.objects.filter(project=project)
	
	app = get_app('project')

	casesforemployee=[]

	for model in get_models(app):
		if model._meta.db_table=="project_rankforemployee":
			for name in model._meta.get_all_field_names():
				if name !="id" and name!="project" and name!="totalRank" and name!="employee" and name!="count":
					casesforemployee.append(name)


	if request.method == 'POST':

		if request.POST.get('submitOffer'):
			
			offer_id=request.POST['div']
			offer=Offering.objects.get(id=offer_id)
			offer.is_accepted_by_employer=True
			offer.save()
			project.is_wait_for_employee=True
			project.save()

			#mail(userId=1,kind="contact",text='submitOffer Project.id='+str(projectid))	

			string = "/project/"+str(project.id)
			return render_to_response('alert.html', {'error':"پیغام درخواست انجام پروژه به کارفرما فرستاده شد , شما باید منتظر بمانید",'address':string})
			

		if request.POST.get('message'):
			
			dis = Discussion(project=project,userprofile=userprofile,message=request.POST.get('message'),date=datetime.datetime.now().replace(tzinfo=utc))
			dis.save()
			string="<script type='text/javascript '> window.location.href= '/project/"+str(project.id)+"/discussiontab/';</script>"

			#contactFilter(dis.message,"Discussion",dis.id)

			return HttpResponse(string)



	elif request.method == 'GET':
		
		try:
			projectFile = ProjectFile.objects.get(project=project)
			form['attachedUrl'] = '/static/files/project/'+str(projectFile.id)+'.zip'

		except:
			pass

		

		if project.is_running==True:

			offerlist=[]

			for offer in Offering.objects.filter(project=project):
				offerlist.append(offer)

			form['offerlist']=offerlist


			form['cases']=casesforemployee
			form['is_employer']=True

			valueCases={}

			#if project.employee.rankForEmployee:
			#	for name, val in project.employee.rankForEmployee:
			#		if name !="id" and name!="project" and name!="totalRank" and name!="employer" and name!="count":
			#			valueCases[name]=val

			form['valueCases']=valueCases
			form['project']=project

			files=project.files.all().order_by('uploadTime').reverse()#[0:5]
			allfiles=[]
			if files.count():
				for f in files:
					allfiles.append(f)

				form['files']=allfiles
				form['is_file_uploaded']=True
			else:
				form['is_file_uploaded']=False


			form['error']="شما پیمانکار خود را انتخاب کرده اید"
			form['done']=True
		else:



			seconds=project.offerTime+timedelta(hours=project.hourTimeForOffer)-datetime.datetime.now().replace(tzinfo=utc)#datetime.datetime.now().replace(tzinfo=utc).replace(tzinfo=utc)
			seconds=seconds.total_seconds()


			#print project.offerTime
			#print datetime.datetime.now().replace(tzinfo=utc)

			timediff = str(timedelta(seconds=seconds))

			form['time_remain_forOffer']=timediff
			form['seconds_remain_forOffer']=seconds
			form['hours_remain_forOffer']=floor(seconds/3600)

			if (seconds>0):
				form['is_time_remain']=True
				

			else:
				form['is_time_remain']=False



			offerlist=[]

			for offer in Offering.objects.filter(project=project):
				if offer.is_accepted_by_employer:
					form['acceptedOffer']=offer
				else:
					offerlist.append(offer)

			form['offerlist']=offerlist
			

		s = 0.

		count=0
		for offer in offerlist:
			s  = s + offer.totallValue
			count  = count + 1
			if request.user.userprofile == offer.offerer:
				form['offered']=True
				form['youroffer']=offer

		if count:
			form['averageOfferValue'] = s/count
		else:
			form['averageOfferValue'] = 0

		yourofferimages = 0
		for offer in offerlist:
			if offer.is_accepted_by_employee:
				yourofferimages=offer.image
		if yourofferimages != 0:
			form['images']=yourofferimages.split(',')

		discussions = Discussion.objects.filter(project=project)
		return render_to_response('projectForEmployer.html', {'form': form,'discussions':discussions},context_instance=RequestContext(request))







def projectForOther(request,projectid,form):
	form['offer_finished']=False
	project=Project.objects.get(id=projectid)
	employer=User.objects.get(id=project.employer_id)
	offerlist=Offering.objects.filter(project=project)
	#account=userprofile.account

	casesforemployer=[]
	app = get_app('project')

	for model in get_models(app):
		if model._meta.db_table=="project_rankforemployer":
			for name in model._meta.get_all_field_names():
				if name !="id" and name!="project" and name!="totalRank" and name!="employee" and name!="count":
					casesforemployer.append(name)


	if request.method == 'POST':

		
		if not request.user.is_authenticated():
			return render_to_response('alert.html', {'error':"لطفا ابتدا وارد شوید",'address':'/login/'})
		
		userprofile=UserProfile.objects.get(id=request.user.id)

		if not userprofile.is_designer :
				return render_to_response('alert.html', {'error':"برای ثبت پیشنهاد باید به عنوان طراح ثبت نام کرده و وارد سایت شوید!"})
					

		if 'upload' in request.POST:
			return views.upload(request,project.id)

		if request.POST.get('accept'):
			return acceptOfferByEmployee(project)
		if request.POST.get('cancel'):
			return cancelOfferByEmployee(project)


		if request.POST.get('message'):
			dis = Discussion(project=project,userprofile=userprofile,message=request.POST.get('message'),date=datetime.datetime.now().replace(tzinfo=utc))
			dis.save()

			#contactFilter(dis.message,"Discussion",dis.id)

			#mail(userId=project.employer.id,kind="discussion",text='http://www.zirend.ir/project/'+str(project.id))

			string='/project/'+str(project.id)+'/discussiontab/'
			return HttpResponseRedirect(string)

		else:

			if not userprofile.is_designer :
				return render_to_response('alert.html', {'error':"برای ثبت پیشنهاد باید به عنوان طراح ثبت نام کرده و وارد سایت شوید!"})
			
			if project.is_running or project.is_failed or project.is_finished or project.is_canceled or project.is_wait_for_employee or request.user.id==project.employer.id:
				return render_to_response('alert.html', {'error':"زمان ثبت پیشنهاد به اتمام رسیده است",'address':'-1'})
			else:
				seconds=datetime.timedelta(hours=project.hourTimeForOffer)+project.offerTime-datetime.datetime.now().replace(tzinfo=utc)
    			seconds=seconds.total_seconds()
    			if seconds < 0:
    				return render_to_response('alert.html', {'error':"زمان ثبت پیشنهاد به اتمام رسیده است",'address':'-1'})


    		for offer in Offering.objects.filter(project=project):
    			if offer.offerer == userprofile:
    				return render_to_response('alert.html', {'error':"شما قبلا برای این پروژه پیشنهاد ثبت کرده اید",'address':'-1'})
    			else:
    				continue

    		try:
    			int(request.POST.get('value'))
    			int(request.POST.get('totallValue'))
    			int(request.POST.get('offerDay'))
    			
    		except:
				return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':'-1'})    			
    		try:
    			bayane=int(request.POST.get('bayane'))
    		except:
    			bayane=0


    		value=request.POST.get('value')
    		totallValue=request.POST.get('totallValue')
    		offerDay=request.POST.get('offerDay')
    		image_url=request.POST.get('image')
    		#image_name=os.path.basename(image_url)
    		#extension = os.path.splitext(image_url)[1]
    		#copyfile(image_url, '/static/offeringfiles')
    		#image=str(project.id) + str(offer.id) + extension
    		#os.rename('/static/offeringfiles/' + image_name, image)

    		if int(offerDay)<0 or int(bayane)<0 :
    			return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':'-1'})
    		else:
    			pass

			text=request.POST.get('text')


			try:
				int(value)
				int(totallValue)
			except:
				address = '/project/'+str(project.id)
				return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':address})

			if int(value)<0 or int(totallValue)<0:
				address = '/project/'+str(project.id)
				return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':address})
			else:
				offer=Offering(bayane=bayane,offerer=userprofile,project=project,text=text,offerTime=datetime.datetime.now().replace(tzinfo=utc),offerDay=offerDay,value=value,totallValue=totallValue,image=image_url)

				notif=Notification(sender="admin",receiver=project.employer,text=u'برای پروژه شما پیشنهاد جدیدی ثبت شده است.',sentTime=datetime.datetime.now().replace(tzinfo=utc))
				notif.save()
				
			offer.save()


			#if Offering.objects.filter(project=project).count()==1:
				#mail(userId=1,kind="contact",text='offer Project.id='+str(project.id))

			#contactFilter(offer.text,"offer",offer.id)

			related=relatedProjects(is_crowd=False,project_id=project.id,is_employer=False)
			related.save()
			userprofile.relatedProjects.add(related)
			userprofile.save()


			form['offered']=True
			string= "/project/"+str(project.id)
			return render_to_response('alert.html', {'error':"پیشنهاد شما با موفقیت ذخیره شد.شما میتوانید در صورت نیاز پیشنهاد خود را در همین قسمت ویرایش کنید.",'address':string})
		




	elif request.method == 'GET':
		try:
			projectFile = ProjectFile.objects.get(project=project)
			form['attachedUrl'] = '/static/files/project/'+str(projectFile.id)+'.zip'
		except:
			pass
		
		try:
			UserProfile.objects.get(id=request.user.id)
		except:
			seconds=datetime.timedelta(hours=project.hourTimeForOffer)+project.offerTime-datetime.datetime.now().replace(tzinfo=utc)

			#print "times"+str(project.hourTimeForOffer)
			seconds=seconds.total_seconds()
			timediff = str(datetime.timedelta(seconds=seconds))

			form['time_remain']=timediff[:timediff.find('.')]
			form['seconds_remain']=seconds
			
			

			if (seconds>0):
				form['is_time_remain']=True
				

			else:
				form['is_time_remain']=False

			form['offerlist']=offerlist

			form['offered']=False
			s = 0
			count=0
			for offer in offerlist:
				s  = s + offer.totallValue
				count  = count + 1
				try:
					if request.user.userprofile == offer.offerer:
						form['offered']=True
						form['youroffer']=offer
				except:
					form['offered']=False


			if count:
				form['averageOfferValue'] = s/count
			else:
				form['averageOfferValue'] = 0

			if project.is_wait_for_employee:
				offer=Offering.objects.get(id=project.choosedOffer_id)
				form['choosedOffer']=offer
				

			discussions = Discussion.objects.filter(project=project)


			return render_to_response('projectForOthers.html', {'form': form , 'discussions':discussions ,'login':False },context_instance=RequestContext(request))


		userprofile=UserProfile.objects.get(id=request.user.id)
		discussions = Discussion.objects.filter(project=project)

		
		form['offerlist']=offerlist
		
		if project.employee:
			if project.employee.userprofile==userprofile:
				
				for offer in offerlist:
					if request.user.userprofile == offer.offerer:
						form['youroffer']=offer
						yourofferimages=offer.image
					if offer.is_accepted_by_employee:
						form['offer_finished']=True

				form['images']=yourofferimages.split(',')
				valueCases={}
				form['cases']=casesforemployer
				form['is_employer']=False

				form['project']=project
				form['valueCases']=valueCases

				files=project.files.all().order_by('uploadTime').reverse()
				form['files']=files
				return render_to_response('projectForEmployeeAfterStart.html', {'form': form , 'login':True , 'user':request.user } ,context_instance=RequestContext(request))
			else:
				return render_to_response('projectForOthers.html', {'login':True, 'user':request.user , 'form': form,'discussions':discussions},context_instance=RequestContext(request))




		else:

			seconds=datetime.timedelta(hours=project.hourTimeForOffer)+project.offerTime-datetime.datetime.now().replace(tzinfo=utc)

			#print datetime.datetime.now().replace(tzinfo=utc).replace(tzinfo=utc)
			#print project.hourTimeForOffer
			seconds=seconds.total_seconds()
			timediff = str(datetime.timedelta(seconds=seconds))

			form['time_remain']=timediff[:timediff.find('.')]
			form['seconds_remain']=seconds
			

			if (seconds>0):
				form['is_time_remain']=True
				

			else:
				form['is_time_remain']=False

			form['offerlist']=offerlist

			form['offered']=False
			s = 0.

			count=0
			for offer in offerlist:
				s  = s + offer.totallValue
				count  = count + 1
				if request.user.userprofile == offer.offerer:
					form['offered']=True
					form['youroffer']=offer

			if count:
				form['averageOfferValue'] = s/count
			else:
				form['averageOfferValue'] = 0

			if project.is_wait_for_employee:
				offer=Offering.objects.get(id=project.choosedOffer_id)
				form['choosedOffer']=offer



			discussions = Discussion.objects.filter(project=project)

			return render_to_response('projectForOthers.html', {'form': form ,'login':True, 'user':request.user , 'discussions':discussions },context_instance=RequestContext(request))



def changeOffer(request,projectid,offerid):

	

	project=Project.objects.get(id=projectid)

	userprofile=UserProfile.objects.get(id=request.user.id)

	offer=Offering.objects.get(id=offerid)



	form={}

	form['youroffer']=offer
	if request.method=="POST":

		if project.is_running or project.is_failed or project.is_finished or project.is_canceled or project.is_wait_for_employee or request.user.id==project.employer.id :
			return render_to_response('alert.html', {'error':"زمان ثبت پیشنهاد به اتمام رسیده است",'address':'-1'})

		try:
			int(request.POST.get('value'))
			int(request.POST.get('totallValue'))
			int(request.POST.get('offerDay'))
		except:
			address = '/project/'+str(project.id)
			return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':address})

		offer=Offering.objects.get(id=offerid)
		value=request.POST.get('value')
		totallValue= request.POST.get('totallValue')
		offerDay=request.POST.get('offerDay')
		text=request.POST.get('text')
		image_url=request.POST.get('image')
		#percentage=request.POST.get('percentage')


		if int(offerDay)<0 or int(offerDay)<=0:
			return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':'-1'})

		offer.text=text
		offer.offerDay=offerDay
		offer.image=image_url

		

		if int(value)<0 or int(totallValue)<0:
			address = '/project/'+str(project.id)
			return render_to_response('alert.html', {'error':"اطلاعات وارد شده صحیح نمیباشد",'address':address})
		else:
			offer.value=value
			offer.totallValue=totallValue


		offer.save()
		#contactFilter(offer.text,"offer",offer.id)

		form['offered']=True
		address = '/project/'+str(project.id)
		return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':address})
	
		#string="<script type='text/javascript '> window.alert ('done' );window.location.href= '/project/"+str(project.id)+"'; </script>"
		#return HttpResponse(string)

	elif request.method=="GET":
		form['user']=request.user
		form['project']=project
		form['offerDay']=offer.offerDay
		form['value']=offer.value
		form['totallValue']=offer.totallValue
		form['text']=offer.text


		seconds=datetime.timedelta(hours=project.hourTimeForOffer)+project.offerTime-datetime.datetime.now().replace(tzinfo=utc)#.replace(tzinfo=utc)

		seconds=seconds.total_seconds()
		timediff = str(datetime.timedelta(seconds=seconds))
		form['time_remain']=timediff[:timediff.find('.')]
		form['seconds_remain']=seconds

		if (seconds<0):
			form['is_time_remain']=True
		else:
			form['is_time_remain']=False


		return render_to_response("changeOffer.html",{'form':form},context_instance=RequestContext(request))





def acceptOfferByEmployee(project):

	

	#print("acceptOfferByEmployee project.id = "+ str(project.id) + " " + str(datetime.datetime.now().replace(tzinfo=utc)) )


	#admin=UserProfile.objects.get(is_admin=True)
	offer=Offering.objects.get(id=project.choosedOffer_id)

	if offer.is_accepted_by_employee:
		address = '/project/'+str(project.id)
		return render_to_response('alert.html', {'error':"خطایی رخ داده است لطفا با عوامل سایت تماس حاصل فرمایید",'address':address})

	if offer.offerer.account.money < int(offer.bayane) :
		address = '/project/'+str(project.id)
		return render_to_response('alert.html', {'error':"شما اعتبار کافی در حساب مالی خود ندارید",'address':address})
	
		#string="<script type='text/javascript '> window.alert ('your account does not have enough money ' );window.location.href= '/project/"+str(project.id)+"'; </script>"
		#return HttpResponse(string)
	else:

		employee=Employee(userprofile=offer.offerer,gainedMoney=0,cashedMoney=offer.bayane)
		employee.save()

		project.employee=employee
		project.is_wait_for_employee=False
		offer.is_accepted_by_employee=True

		offer.offerer.account.money=str (int(offer.offerer.account.money) - int (offer.bayane) )

		activity=AccountActivity(activityType="W",transmitedMoney=str(offer.bayane),transferTime=datetime.datetime.now().replace(tzinfo=utc),description="بیعانه باقیمانده برای انجام پروژه")
		activity.save()
		offer.offerer.account.accountActivity.add(activity)
		offer.offerer.account.save()
		offer.offerer.save()
		offer.save()



		project.endDate=datetime.datetime.now().replace(tzinfo=utc)+datetime.timedelta(days=offer.offerDay)
		project.startDate=datetime.datetime.now().replace(tzinfo=utc)
		project.is_crowd=False
		project.is_running=True
		project.is_active=True
		project.save()

		address = '/project/'+str(project.id)
		#mail(userId=1,kind="contact",text='acceptOfferByEmployee Project.id='+str(project.id))	

		return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':address})

		#string="<script type='text/javascript '> window.alert ('done!' );window.location.href= '/project/"+str(project.id)+"';</script>"
		#return HttpResponse(string)


def cancelOfferByEmployee(project):
	
	

	#print("cancelOfferByEmployee project.id =  "+ str(project.id) + " " + str(datetime.datetime.now().replace(tzinfo=utc)) )


	#admin=UserProfile.objects.get(is_admin=True)
	offer=Offering.objects.get(id=project.choosedOffer_id)

	if offer.is_accepted_by_employee == True:
		address = '/project/'+str(project.id)
		return render_to_response('alert.html', {'error':"خطایی رخ داده است لطفا با عوامل سایت تماس حاصل فرمایید",'address':address})

	project.is_wait_for_employee=False

	offer.is_accepted_by_employee=False
	offer.is_accepted_by_employer=False

	offer.save()

	#message=Message(sender=admin,receiver=project.employer,text='your choosed employee refused to do your project please choose another one',sentTime=datetime.datetime.now().replace(tzinfo=utc))
	#message.save()
	notif=Notification(sender="admin",receiver=project.employer,text=u'کارمند انتخابی شما حاضر به انجام پروژه نشد. در صورت تمایل کارمند دیگری انتخاب فرمایید.',sentTime=datetime.datetime.now().replace(tzinfo=utc))
	notif.save()


	project.save()

	#mail(userId=1,kind="contact",text='cancelOfferByEmployee Project.id='+str(project.id))	

	address = '/project/'+str(project.id)
	return render_to_response('alert.html', {'error':"با موفقیت انجام شد",'address':address})


