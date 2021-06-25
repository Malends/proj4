from django.urls import path
from django.urls import include

from . import views

urlpatterns = [
    path('add-review/<int:doc_id>/', views.review_write, name='review_write'),
    path('review/', views.review_list, name='review_list'),
    path('success/', views.success, name='success'),
    path('accounts/', include('django.contrib.auth.urls')),
]