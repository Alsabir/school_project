from django import forms
from django.contrib.auth.models import User
from archive import models


class UserRegistrationForm(forms.Form):
	username = forms.CharField(label = 'Имя пользователя', label_suffix = ':')
	password = forms.CharField(label = 'Пароль', label_suffix = ':',widget = forms.PasswordInput)
	first_name = forms.CharField(label = 'Имя', label_suffix = ':', required = False)
	last_name = forms.CharField(label = 'Фамилия', label_suffix = ':',required = False)
	email = forms.EmailField(label = 'Адрес элекронной почты', label_suffix = ':')

	def clean_username(self):
		username = self.cleaned_data['username']
		if User.objects.filter(username = username).count()>0:
			raise forms.ValidationError('Это имя пользователя уже занято: {0}'.format(username))
		return username	


class SendSolutionForm(forms.Form):
	text = forms.CharField(label = 'Решение', label_suffix = ':', required = False, max_length = 1200, strip = True, widget = forms.Textarea)
	image_attached = forms.ImageField(label = 'Приложенная картинка', label_suffix = ':', required = False)

	def clean_image_attached(self):
		text = self.cleaned_data['text']
		image_attached = self.cleaned_data['image_attached']
		if not (text or image_attached):
			raise forms.ValidationError('Оба поля не могут быть пустыми')
		return image_attached	


class EvaluateForm(forms.Form):
	score = forms.IntegerField(label = 'Балл',label_suffix = ':')	
	comment = forms.CharField(label='Комментарий',label_suffix=':', required = False, widget = forms.Textarea)		

	def clean_score(self):
		score = self.cleaned_data['score']
		if score>7 or score<0:
			raise forms.ValidationError('Балл должен быть целым числом от 0 до 7')
		if int(score) != score :
			raise forms.ValidationError('Балл должен быть целым числом.')
		return score
		



			
