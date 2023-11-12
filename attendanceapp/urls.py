from django.urls import path
from .views import AttendanceList, AddItem, EditItem, DeleteItem, RegisterAccount
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', AttendanceList.as_view(), name='top'),
    path('add-item/', AddItem.as_view(), name='add-item'),
    path('edit-item/<int:pk>', EditItem.as_view(), name='edit-item'),
    path('delete-item/<int:pk>', DeleteItem.as_view(), name='delete-item'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterAccount.as_view(), name='register')
]
