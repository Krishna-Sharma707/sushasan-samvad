from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name="register"),
    path('upload_meeting/', views.upload_meeting),
    path('meetings/<int:meeting_id>', views.meeting),
    path('district/<int:dist_id>', views.district, name='district'),
    path('village/<int:village_id>', views.village, name='village')
]
