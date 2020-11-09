#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#encoding:UTF-8
from django import forms
from django.utils.translation import ugettext as _
from django.core.validators import validate_email
from django.contrib.auth.forms import AuthenticationForm
from freeDesigner.models import UserProfile
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple


error_messages={}

error_messages['invalid']='عدد وارد شده برای کپچا اشتباه میباشد'
error_messages['invalid_number']='لطفا برای فیلد کپچا یک عدد وارد کنید'

class NewProjectForm(forms.Form):    
    title = forms.CharField( max_length=100) 
    offerDay = forms.IntegerField(initial=1)
    
    description = forms.CharField(widget=forms.Textarea)
    #licence = forms.ModelMultipleChoiceField(queryset=Licence.objects.all(),widget=CheckboxSelectMultiple,required=False)
    dayTimeForOffer=forms.IntegerField(initial=0)
    hourTimeForOffer=forms.IntegerField(initial=1)
    is_public=forms.BooleanField(required=False)

    
    def clean_description(self): 
        description = self.cleaned_data['description']
        num_words = len(description.split()) 
        if num_words  <1: 
            raise forms.ValidationError("تعداد کلمات کم") 
        return description

    def clean_offerDay(self): 
        offerDay = self.cleaned_data['offerDay']
        if int(offerDay)<0:
            raise forms.ValidationError("عدد منفی") 
        return offerDay

    

    def clean_dayTimeForOffer(self): 
        dayTimeForOffer = self.cleaned_data['dayTimeForOffer']
        if int(dayTimeForOffer)<0:
            raise forms.ValidationError("عدد منفی") 
        return dayTimeForOffer

    def clean_hourTimeForOffer(self): 
        hourTimeForOffer = self.cleaned_data['hourTimeForOffer']
        if int(hourTimeForOffer)<0:
            raise forms.ValidationError("عدد منفی") 
        return hourTimeForOffer
    
    
        
        
class uploadForm(forms.Form):    
    description = forms.CharField(widget=forms.Textarea)
    f = forms.FileField()
    
    def clean_file(self): 
        f = self.cleaned_data['f']
        if f.name[-4:]!=".zip": 
            raise forms.ValidationError("لطفا فایل با فرمت زیپ وارد کنید") 
        return f  
  

    
    
class MortgageForm(forms.Form):
    amount=forms.IntegerField()
    
    def clean_amount(self):
        
        a=int ( self.cleaned_data['amount'] )
        if a<0:
            raise forms.ValidationError("عدد منفی")
        return a
    
    
    
class IncreaseTimeForm(forms.Form):
    day=forms.IntegerField(initial=1)
    month=forms.IntegerField(initial=0)
    
    
    def clean_day(self):
        
        day=self.cleaned_data['day']
        
        if day<0:
            raise forms.ValidationError("عدد منفی")
        return day
    
    def clean_month(self):
        
        month=self.cleaned_data['month']
        
        
        if month<0:
            raise forms.ValidationError("عدد منفی")
        return month
    

