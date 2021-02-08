from django.urls import path
from . import views

app_name = 'app'
urlpatterns = [
    path(r'user_create/', views.UserCreate.as_view(), name='user_create'),
    path(r'user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path(r'user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path(r'', views.CustomLoginView.as_view(), name='login'),
]