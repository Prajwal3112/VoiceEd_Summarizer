from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('start_recording/', views.start_recording, name='start_recording'),
    path('stop_recording/', views.stop_recording, name='stop_recording'),
    path('convert/', views.speech_to_text, name='convert'),
    path('records/', views.list_records, name='list_records'),
    path('records/<int:record_id>/', views.view_transcription, name='view_transcription'),
]