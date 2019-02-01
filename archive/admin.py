from django.contrib import admin
from .models import Problem, Solution, TypeOfProblem, Evaluation, ProfileData



class SolutionInline(admin.TabularInline):
    model = Solution
    extra = 0

class EvaluationInline(admin.TabularInline):
    model = Evaluation
    extra = 0    

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title','description','image_attached')
    inlines = [SolutionInline]



@admin.register(Solution)
class SolutionAdmin(admin.ModelAdmin):
	exclude = []
	inlines = [EvaluationInline]

@admin.register(ProfileData)
class ProfileDataAdmin(admin.ModelAdmin):
	exclude = [] 
	

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    exclude = []




