from django.urls import path

from lists import views

urlpatterns = [
    path('', views.ListViewSet.as_view({'get': 'list', 'post': 'create'}), name='lists'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('item/<slug:slug>/', views.ItemViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='item_detail'),
    path('<slug:slug>/', views.ListViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='list_detail'),
    path('<slug:slug>/items/', views.ItemViewSet.as_view({'post': 'create'}), name='items'),
]
