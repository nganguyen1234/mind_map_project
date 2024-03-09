from django.urls import path
from . import views


urlpatterns = [
    path('',views.getData),
    path('upload-file/',views.FileUploadAPIView.as_view())

]