#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#encoding:UTF-8
from django import forms
from django.utils.translation import ugettext as _
from django.core.validators import validate_email
from django.contrib.auth.forms import AuthenticationForm
from freeDesigner.models import UserProfile,Chat
from django.forms.fields import MultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple
from django.forms import ModelForm

GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)
MONTH_CHOICES = (
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
)




class RegisterForm(forms.Form):
    error_messages = {
        'duplicate_username': ("کاربری با این نام کاربری وجود دارد"),
        'password_mismatch': ("پسوردهای وارد شده با هم تطابق ندارند"),
    }
    

    user_name = forms.CharField(
        label = _('User Name'), 
        min_length = 2, 
        max_length = 30,
        widget = forms.TextInput(attrs={
            'placeholder':_('username'),
            'class': 'span6 ',
            'autocomplete' :'off',
            
            
            
        })
    )
    
    email = forms.EmailField(
        label = _('E-Mail'),
        min_length = 5,
        widget = forms.TextInput(attrs={
            'placeholder': _('Your email address'),
            'type': 'email',
            'class': 'span6 ',
            'autocomplete' :'off',
        })
    )
    
    password = forms.CharField(
        label = _('Password'),
        min_length = 3,
        max_length = 30,
        widget = forms.PasswordInput(attrs={
            'placeholder':_('Password'),
            'class': 'span6 ',
            'autocomplete' :'off',
        })
    )
    confirm_password = forms.CharField(
        label = _('Re-type password'),
        min_length = 3,
        max_length = 30,
        widget = forms.PasswordInput(attrs={
            'placeholder':_('Re-type password'),
            'class': 'span6',
            
        })
    )
    
    def clean_user_name(self):
        
        username = self.cleaned_data['user_name']
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=username) 
        except User.DoesNotExist:
            return username
        else:
            # E-mail is a uniqe field 
            raise forms.ValidationError('کاربری با این نام کاربری وجود دارد')


    def clean_email(self):
        
        email = self.cleaned_data['email']
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email=email) 
        except User.DoesNotExist:
            return email
        else:
            # E-mail is a uniqe field 
            raise forms.ValidationError('کاربری با این ایمیل وجود دارد')

    def clean_password(self):
        password = self.cleaned_data['password']
        
        # Check strog password
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data['confirm_password']
        if confirm_password != self.cleaned_data['password']:
            raise forms.ValidationError("پسوردهای وارد شده با هم تطابق ندارند")
        return confirm_password


#     first_name = forms.CharField(
#         label = _('First Name'), 
#         min_length = 2, 
#         max_length = 30,
#         widget = forms.TextInput(attrs={
#             'placeholder':_('First Name'),
#             'class': 'span6 required',
#             'required': '',
#         })
#     )
#     
#     
# 
#     last_name = forms.CharField(
#         label = _('Last Name'),
#         min_length = 2,
#         max_length = 30,
#         widget = forms.TextInput(attrs={
#             'placeholder':_('Last Name'),
#             'class': 'span6 required',
#             'required': '',
#         })
#     )
#     
#     
#     gender = forms.ChoiceField(choices=GENDER_CHOICES)
# 
#     month = forms.ChoiceField(choices=MONTH_CHOICES,
#         widget=forms.Select(attrs={
#             'class': 'span4',
#         })
#     )
# 
#     day = forms.CharField(
#         label = _('Day'),
#         min_length = 1,
#         max_length = 2,
#         widget = forms.TextInput(attrs={
#             'placeholder':_('Day'),
#             'class': 'span4',
#             'required': '',
#         })
#     )
# 
#     year = forms.CharField(
#         label = _('Year'),
#         min_length = 4,
#         max_length = 4,
#         widget = forms.TextInput(attrs={
#             'placeholder':_('Year'),
#             'class': 'span4',
#             'required': '',
#         })
#     )
# 
#     def clean_day(self):
#         day = int(self.cleaned_data['day'])
#         if (day > 31 or day < 1):
#             raise forms.ValidationError(_('Invalid date'))
#         return day
# 
#     def clean_month(self):
#         month = int(self.cleaned_data['month'])
#         if (month > 12 or month < 1):
#             raise forms.ValidationError(_('Invalid date'))
#         return month
# 
#     def clean_year(self):
#         year = int(self.cleaned_data['year'])
#         if (year > 2012 or year < 1900):
#             raise forms.ValidationError(_('Invalid date'))
#         return year

    


class LoginForm(forms.Form):
    #errors ="user with this password and username dosen't exist"
    errors =""
    username = forms.CharField(
        label = _('User Name'), 
        min_length = 2, 
        max_length = 30,
        widget = forms.TextInput(attrs={
            'placeholder':_('username'),
            'class': 'span6 required',
            'required': '',
        })
    )
    password = forms.CharField(
        label = _('Password'),
        min_length = 6,
        max_length = 30,
        widget = forms.PasswordInput(attrs={
            'placeholder':_('Password'),
            'class': 'span6 required',
            'required': '',
        })
    )

    set_username=''
    set_password=''





class MessageForm (forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    def clean_text(self): 
        text = self.cleaned_data['text']
        num_words = len(text.split()) 
        if num_words  <1:
            raise forms.ValidationError("not enough words") 
        return text
  

class photoForm (forms.Form):
    photo = forms.ImageField()
    def clean_photo(self): 

        import PIL
        from PIL import Image

        image = Image.open(self.photo)
        if image._size > 4*1024*1024:
            raise ValidationError("Image file too large ( > 4mb )")
        return image




    
    
    
class AccountForm(forms.Form):    
    text = forms.IntegerField()
    def clean_text(self): 

        text = int ( self.cleaned_data['text'] )
        
        if text<0:
            raise forms.ValidationError("Negative Number")

        return text



