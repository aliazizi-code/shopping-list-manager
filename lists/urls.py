from django.urls import path

from lists import views

urlpatterns = [
    path('lists/', views.ListViewSet.as_view({'get': 'list', 'post': 'create'}), name='list_create'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('item/<slug:slug>/', views.ItemViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}),
         name='item_detail'),
    path('list/<slug:slug>/',
         views.ListViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='list_detail'),
    path('list/<slug:slug>/items/', views.ItemViewSet.as_view({'post': 'create'}), name='items'),
]
