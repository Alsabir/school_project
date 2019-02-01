from django.urls import path
from archive import views


urlpatterns = [
	path('',views.index, name = 'index'),
	path('problems/',views.ProblemListView.as_view(),name = 'problems'),
	path('problem/<int:pk>',views.ProblemDetailView.as_view(),name = 'problem-detail'),
	path('profile/',views.profile_page, name = 'profile'),
	path('profile/problems-solved/',views.UserSolutionsListView.as_view(),name = 'user-solution-list'),
	path('solutions-to-check/',views.AdminSolutionsListView.as_view(),name = 'admin-solution-list'),
	path('solution/<int:pk>/',views.SolutionDetailView.as_view(),name = 'solution-detail'),
	path('accounts/registration/',views.user_registration,name = 'registration'),
	path('problems/create/', views.ProblemCreate.as_view(), name='problem-create'),
	path('problems/<int:pk>/update/', views.ProblemUpdate.as_view(), name='problem-update'),
	path('problems/<int:pk>/delete/', views.ProblemDelete.as_view(), name='problem-delete'),
	path('type_of_problems/create/', views.TypeOfProblemCreate.as_view(), name='type-of-problem-create'),
    path('type_of_problems/<int:pk>/update/', views.TypeOfProblemUpdate.as_view(), name='type-of-problem-update'),
    path('type_of_problems/<int:pk>/delete/', views.TypeOfProblemDelete.as_view(), name='type-of-problem-delete'),
    path('type_of_problems',views.TypeOfProblemListView.as_view(),name = 'types-list'),
    path('send_solution/<int:pk>/',views.send_solution, name = 'send-solution'),
    path('evaluate/<int:pk>/', views.evaluate, name = 'evaluate'),
    path('leaders/',views.table_of_leaders, name = 'leaders'),
    path('recommendations/', views.recommendations, name = 'recommendations')
]
