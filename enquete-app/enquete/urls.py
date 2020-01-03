from django.urls import path

from . import views

app_name = 'enquete'

urlpatterns = [
    # アンケート一覧画面
    path('', views.EnqueteListView.as_view(), name='list'),
    # アンケート作成画面
    path('create/', views.EnqueteCreateView.as_view(), name='create'),
    path('<int:page_num>/', views.EnqueteListView.as_view(), name='page'),
    # アンケート詳細画面
    path('<str:uuid>/', views.EnqueteDetailView.as_view(), name='detail'),
    # アンケート回答画面
    path('<str:uuid>/answer/', views.EnqueteAnswerView.as_view(), name='answer'),
    # アンケート集計画面
    path('<str:uuid>/totalize/',
         views.EnqueteTotalizeView.as_view(), name='totalize'),
    # アンケート回答修正画面
    path('<str:uuid>/<int:member_id>/',
         views.EnqueteAnswerUpdateView.as_view(), name='answer_update'),
]
