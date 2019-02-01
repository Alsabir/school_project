from django.db import models
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.urls import reverse
import json
from django.db.models.signals import post_save,pre_save,pre_delete
from django.dispatch import receiver
# Create your models here.	




class ProfileData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null = True)
    total_score = models.PositiveIntegerField(default = 0)
    problems_solved = models.TextField(blank = True)
    favourite_problem_type = models.TextField(blank = True, default = '{}')

    def __str__(self):
    	return str(self.user)

#https://stackoverflow.com/questions/22340258/django-list-field-in-model
#https://stackoverflow.com/questions/16455777/python-count-elements-in-a-list-of-objects-with-matching-attributes    

class TypeOfProblem(models.Model):
	name = models.CharField(max_length=200, help_text="Введите тип задачи")
    
	def __str__(self):
		return self.name




class Problem(models.Model):

	title = models.CharField(max_length = 100, help_text = "Введите название задачи",default = 'Без названия')
	date_of_creation = models.DateTimeField(auto_now_add = True)
	image_attached = models.ImageField(upload_to="images_to_problems", null = True, blank = True)
	description = models.TextField(blank = True)
	type_of_problem = models.ManyToManyField(TypeOfProblem)

	class Meta: 
		ordering = ['date_of_creation']
		verbose_name = 'Задача'
		verbose_name_plural = "Задачи"

	def __str__(self):
		return self.title    

	def get_absolute_url(self):
		return reverse('problem-detail', args=[str(self.id)])

#	def count_solutions(self):
#		Solutions.objects.filter()	


		


class Evaluation(models.Model):
	solution = models.OneToOneField('Solution', on_delete = models.CASCADE, null = True)
	examiner = models.ForeignKey(User, on_delete = models.CASCADE,null = True)
	score = models.PositiveSmallIntegerField(validators = [MinValueValidator(0),MaxValueValidator(7)])
	comment = models.TextField(blank = True)
	date_of_creation = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return '{0} by {1}'.format(self.solution.problem.title,self.solution.user)

	class Meta:
		ordering = ['date_of_creation']
		verbose_name = 'Оценивание'
		verbose_name_plural = "Оценивания"
		permissions = (('can_assess','Assess solution'),)	

class Solution(models.Model):
	
	user = models.ForeignKey(ProfileData, on_delete = models.CASCADE, null = True)        
	problem = models.ForeignKey(Problem, on_delete = models.CASCADE, null = True)
	text = models.TextField(blank = True)
	date_of_creation = models.DateTimeField(auto_now_add = True)
	image_attached = models.ImageField(upload_to="images_to_solutions", null = True, blank = True)

	class Meta: 
		ordering = ['date_of_creation']
		verbose_name = 'Решение'
		verbose_name_plural = "Решения"

	def __str__(self):
		return '{0} : {1} ({2})'.format(self.problem.title, self.user, self.date_of_creation)    

	def get_absolute_url(self):
		return reverse('solution-detail', args=[str(self.id)])

	def save(self, *args, **kwargs):
		prev_problems_set = Solution.objects.filter(problem__id = self.problem.id, user = self.user)
		if len(prev_problems_set)==1:
			if prev_problems_set[0].is_checked:
				return True
			else:
				Solution.objects.filter(problem__id = self.problem.id, user = self.user).delete()
		super(Solution,self).save(*args,**kwargs)		

	@property
	def is_checked(self):
		return Evaluation.objects.filter(solution__user = self.user,solution__problem = self.problem).exists()
			



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		ProfileData.objects.create(user=instance, problems_solved = json.dumps([]), favourite_problem_type = json.dumps({}))

@receiver(post_save, sender=User)
def save_user_profile(sender, instance,*args, **kwargs):
	instance.profiledata.save()

@receiver(pre_save, sender = Evaluation)
def change_total_score(sender, instance, *args, **kwargs):
	problems_solved = json.loads(instance.solution.user.problems_solved)
	total_score = instance.solution.user.total_score
	problem_id = instance.solution.problem.id
	fav_problems = json.loads(instance.solution.user.favourite_problem_type)
	if problem_id in problems_solved:
		problems_solved.remove(problem_id)
		total_score -= instance.solution.user.solution_set.filter(problem__id = problem_id)[0].evaluation.score
	else:
		for prob_type in instance.solution.problem.type_of_problem.all():
			fav_problems[str(prob_type.id)] = fav_problems.get(str(prob_type.id),0) + 1	


		
	problems_solved.append(problem_id)
	total_score += instance.score
	instance.solution.user.problems_solved = json.dumps(problems_solved)
	instance.solution.user.total_score = total_score
	instance.solution.user.favourite_problem_type = json.dumps(fav_problems)
	instance.solution.user.save()


@receiver(pre_delete, sender = Evaluation)
def update_profile(sender, instance, using, *args, **kwargs):
	problems_solved = json.loads(instance.solution.user.problems_solved)
	total_score = instance.solution.user.total_score
	problem_id = instance.solution.problem.id
	fav_problems = json.loads(instance.solution.user.favourite_problem_type)
	problems_solved.remove(problem_id)
	total_score -= instance.solution.user.solution_set.filter(problem__id = problem_id)[0].evaluation.score
	for prob_type in instance.solution.problem.type_of_problem.all():
		fav_problems[str(prob_type.id)] = fav_problems.get(str(prob_type.id),1) - 1
		if fav_problems[str(prob_type.id)]==0:
			del fav_problems[str(prob_type.id)]	

	instance.solution.user.problems_solved = json.dumps(problems_solved)
	instance.solution.user.total_score = total_score
	instance.solution.user.favourite_problem_type = json.dumps(fav_problems)
	instance.solution.user.save()











