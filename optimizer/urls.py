from django.urls import path
from . import views

urlpatterns =[
    path('add-location/', views.add_location, name='add_location'),
    path('locations/',views.location_list,name='location_list'),
    path('generate-edges/',views.generate_edges, name='generate_edges'),
    path('find-route/',views.find_route, name='find_route')
]