from django.urls import path
from .views import (PostsList, PostDetail, NewsFilter, NewsCreateView, ArticleCreateView, NewsUpdateView,
                    ArticleUpdateView, ArticleDeleteView, NewsDeleteView, CategoryListView, subscribe, subscriptions)

urlpatterns = [
    path('', PostsList.as_view(), name='news'),
    path('<int:pk>/', PostDetail.as_view(), name='post_id'),
    path('articles/<int:pk>/', PostDetail.as_view(), name='post_id'),
    path('search/', NewsFilter.as_view(), name='search'),
    path('create/', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>/edit/', NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete/',   NewsDeleteView.as_view(), name='news_delete'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='articles_edit'),
    path('articles/create/', ArticleCreateView.as_view(), name='articles_create'),
    path('articles/<int:pk>/delete/', ArticleDeleteView.as_view(), name='articles_delete'),
    path('categories/<int:pk>/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/subscribe', subscribe, name='news/subscribe_category'),
    path('subscriptions/', subscriptions, name='subscriptions'),

]
