from archive.models import ProfileData, Problem, Solution, Evaluation, TypeOfProblem
from archive import forms

from django.views import generic
import json
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.models import User

def index(request):
	"""View function for home page of site."""

	# Generate counts of some of the main objects
	num_problems = Problem.objects.all().count()
    
    
	# The 'all()' is implied by default.    
	num_users = ProfileData.objects.count()
    
	context = {
		'num_problems': num_problems,
		'num_users': num_users,
	}

	# Render the HTML template index.html with the data in the context variable
	return render(request, 'index.html', context=context)


class ProblemListView(LoginRequiredMixin,generic.ListView):
	model = Problem
	#queryset = Problem.objects.filter(...)

class TypeOfProblemListView(PermissionRequiredMixin,generic.ListView):
	permission_required = 'can_assess'
	model = TypeOfProblem


class ProblemDetailView(LoginRequiredMixin,generic.DetailView):
	model = Problem

@login_required
def profile_page(request):
	list_of_problems = None
	if request.user.profiledata.problems_solved:
		problems_solved = json.loads(request.user.profiledata.problems_solved)
		list_of_problems = [Problem.objects.get(id = id) for id in problems_solved]
		list_of_solutions = [Solution.objects.get(problem = problem, user__user = request.user) for problem in list_of_problems]

	dict_of_favourites = json.loads(request.user.profiledata.favourite_problem_type)
	if dict_of_favourites:
		list_of_fav_types = sorted(dict_of_favourites, key = dict_of_favourites.__getitem__, reverse = True)	
		max_solved_type_number = dict_of_favourites[list_of_fav_types[0]]
		most_solved_types = [TypeOfProblem.objects.get(id = list_of_fav_types[0])]
		for i in range(1, len(list_of_fav_types)):
			if dict_of_favourites[list_of_fav_types[i]]!= max_solved_type_number:
				most_solved_types = [TypeOfProblem.objects.get(id = id) for id in list_of_fav_types[:i]]
				break
		else:
			most_solved_types = [TypeOfProblem.objects.get(id = id) for id in list_of_fav_types[:len(list_of_fav_types)]]		
	else:
		most_solved_types = None			

	context = {'user': request.user,'list_of_solutions': list_of_solutions,'most_solved_types': most_solved_types}	






	return render(request, 'profile_page.html', context = context)

class UserSolutionsListView(LoginRequiredMixin,generic.ListView):
	model = Solution
	template_name = 'user_solutions_list.html'
	paginate_by = 5

	def get_queryset(self):
		return Solution.objects.filter(user = self.request.user.profiledata).order_by('date_of_creation')

	#queryset = Problem.objects.filter(...)



class AdminSolutionsListView(PermissionRequiredMixin,generic.ListView):
	permission_required = 'can_assess'
	model = Solution
	template_name = 'admin_solutions_list.html'

	def get_queryset(self):
		return Solution.objects.annotate(Count('evaluation')).order_by('evaluation__count','-date_of_creation')


class SolutionDetailView(LoginRequiredMixin,generic.DetailView):
	model = Solution


class SentTwiceSolutionDetailView(LoginRequiredMixin,generic.DetailView):
	model = Solution
	template_name = 'sent_twice_solution_detail.html'



def user_registration(request):
	if request.method == 'POST':
		registration_form = forms.UserRegistrationForm(request.POST)
		if registration_form.is_valid():
			user = User.objects.create_user(registration_form.cleaned_data['username'],registration_form.cleaned_data['email'],registration_form.cleaned_data['password'])
			user.last_name = registration_form.cleaned_data.get('last_name')
			user.first_name = registration_form.cleaned_data.get('first_name')
			user.save()
			login(request,user)
			return HttpResponseRedirect(reverse('index'))
	else:
		registration_form = forms.UserRegistrationForm()

	context = {
		'form':registration_form
	}	

	return render(request,'registration.html',context)


class ProblemCreate(PermissionRequiredMixin,CreateView):
	permission_required = 'can_assess'
	model = Problem
	fields = ['title','image_attached','description','type_of_problem']	

class ProblemDelete(PermissionRequiredMixin,DeleteView):
	permission_required = 'can_assess'	
	model = Problem
	success_url = reverse_lazy('problems')

class ProblemUpdate(PermissionRequiredMixin,UpdateView):
	permission_required = 'can_assess'
	model = Problem
	fields = ['title','image_attached','description','type_of_problem']	
	success_url = reverse_lazy('problems')


class TypeOfProblemCreate(PermissionRequiredMixin,CreateView):
	permission_required = 'can_assess'
	model = TypeOfProblem
	fields = '__all__'
	success_url = reverse_lazy('types-list')

class TypeOfProblemDelete(PermissionRequiredMixin,DeleteView):
	permission_required = 'can_assess'	
	model = TypeOfProblem
	success_url = reverse_lazy('types-list')

class TypeOfProblemUpdate(PermissionRequiredMixin,UpdateView):
	permission_required = 'can_assess'
	model = TypeOfProblem
	fields = '__all__'
	success_url = reverse_lazy('types-list')


@login_required
def send_solution(request,pk):
	if request.method == 'POST':
		send_solution_form = forms.SendSolutionForm(request.POST)
		if send_solution_form.is_valid():
			user = ProfileData.objects.filter(user = request.user)[0]
			problem = Problem.objects.filter(id = pk)[0]

			solution = Solution.objects.create(user = user, problem = problem, 
				text = send_solution_form.cleaned_data.get('text'), image_attached = send_solution_form.cleaned_data.get('image_attached'))
			status = solution.save()
			if status:
				prev_problems_set = Solution.objects.filter(problem__id = problem.id, user = user)	
				return HttpResponseRedirect(reverse('solution-detail', kwargs = {'pk': prev_problems_set[0].id}))
			else:
				return HttpResponseRedirect(reverse('problems'))		
	else:
		send_solution_form = forms.SendSolutionForm()

	context = {
		'form':send_solution_form
	}	

	return render(request,'send_solution.html',context)

@permission_required('can_assess')
def evaluate(request,pk):
	if request.method == 'POST':
		evaluate_form = forms.EvaluateForm(request.POST)
		if evaluate_form.is_valid():
			solution = Solution.objects.filter(id = pk)[0]
			evaluation = Evaluation.objects.create(examiner = request.user, solution = solution,
				score = evaluate_form.cleaned_data.get('score'), comment = evaluate_form.cleaned_data.get('comment'))
			evaluation.save()
			return HttpResponseRedirect(reverse('admin-solution-list'))
	else:
		evaluate_form = forms.EvaluateForm()

	context = { 'form': evaluate_form}
	return render(request,'evaluate.html',context)			


@login_required
def table_of_leaders(request):
	ordered_list = list(ProfileData.objects.order_by('-total_score').all())
	if len(ordered_list)<=10:
		top_10 = ordered_list
	else:
		top_10 = ordered_list[:10]
	class EnumeratedProfile():
		def __init__(self, position, item):
			self.position = position
			self.item = item

	enumerated_list = [EnumeratedProfile(position,item) for position,item in enumerate(top_10, start = 1)]
	user_profile = ProfileData.objects.get(user = request.user)
	user_position = ordered_list.index(user_profile) + 1
	if user_position <= 10:
		is_in_top_10 = True
	else:
		is_in_top_10 = False	

	context = {'enumerated_list': enumerated_list, 'user_profile': user_profile, 'user_position': user_position, 'is_in_top_10': is_in_top_10}

	return render(request, 'leaders.html', context)



def similarity(user1_problems_set,user2):
	user2_problems_set = set(json.loads(user2.problems_solved))
	return len(user1_problems_set & user2_problems_set) / len(user1_problems_set | user2_problems_set)



@login_required
def recommendations(request):
	user_profile = ProfileData.objects.filter(user = request.user)[0]
	all_users = ProfileData.objects.exclude(user = request.user)
	m_user_problems_set = set(json.loads(user_profile.problems_solved))

	if len(m_user_problems_set) == 0:
		context = {'recommendations' : None}			

		return render(request, 'recommendations.html', context)

	similarity_to = {}
	for user in all_users:
		similarity_to[user] = similarity(m_user_problems_set, user)

		
	problems_set = set([problem.id for problem in Problem.objects.all()])
	problems_set = problems_set - m_user_problems_set
	problem_rating_for_user = []



	for problem_id in problems_set:
		likes = 0
		people_solved = 0
		for solution in Problem.objects.filter(id = problem_id)[0].solution_set.all():
			if len(Evaluation.objects.filter(solution = solution)) !=0 :
				likes += similarity_to[solution.user]
				people_solved += 1
		if people_solved > 0:
			problem_rating_for_user.append((Problem.objects.get(id = problem_id),likes/people_solved))
		
	recommendations = [item[0] for item in sorted(problem_rating_for_user, key = lambda a: a[1], reverse = True)][:5]

	context = {'recommendations' : recommendations}			
	return render(request, 'recommendations.html', context)