import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Exists, OuterRef
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from .filter import PostFilter
from .models import Post, PostCategory, Category, Subscription

logger = logging.getLogger(__name__)


class PostsList(ListView):
    model = Post
    ordering = '-created_at'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        logger.debug(f"Параметры фильтрации: {self.request.GET}")
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        return context

    def my_view(self, request):
        filtered_queryset = PostFilter(request.GET, queryset=Post.objects.all()).qs

        paginator = Paginator(filtered_queryset, 5)
        page_number = request.GET.get('page')

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(request, 'news.html', {'page_obj': page_obj})


class PostDetail(DetailView):
    model = Post
    template_name = 'post_id.html'
    context_object_name = 'post'


class NewsFilter(FilterView):
    model = Post
    filterset_class = PostFilter
    ordering = '-created_at'
    context_object_name = 'content'
    template_name = 'search.html'
    current_date = datetime.now()
    formatted_date = current_date.strftime('%d-%m-%Y')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['filterset'] = self.filterset
        context['time_now'] = datetime.utcnow()
        first_post_category = PostCategory.objects.first()
        context['first_post_category'] = first_post_category

        # Проверить, что есть хотя бы одна запись в модели PostCategory
        if first_post_category:
            first_post_created_at = first_post_category.post.created_at
            context['time_now'] = first_post_created_at
        else:
            # context['time_now'] = datetime.utcnow().strftime('%d-%m-%Y')
            context['time_now'] = datetime.utcnow()
            context['news'] = Post.objects.all()
            context['filterset'] = self.filterset
        return context

    def get(self, request, *args, **kwargs):
        # Логика вашего представления

        # return super().get(request, 'news/search.html', {}, **kwargs)
        return super().get(request, *args, **kwargs)

    def has_permission(self):
        perms = self.get_permission_required()
        return self.request.user in self.get_object().authors.all()

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class NewsCreateView(CreateView):
    raise_exception = True
    # permission_required = ('news.post_add',)
    model = Post
    fields = ['title', 'content', 'categories', 'post_type', 'post_author']
    template_name = 'news_create.html'
    extra_context = {'page_title': 'Разместите тут Вашу новость:'}

    def form_valid(self, form):
        form.instance.post_type = 'N'  # Устанавливаем значение поля в зависимости от страницы
        self.object = form.save(commit=False)
        self.object.post_type = form.instance.post_type
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'новость'  # Передача post_type в контекст шаблона
        return context


class NewsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.post_change',)
    model = Post
    fields = ['title', 'content', 'categories', 'post_type']
    template_name = 'news_create.html'
    extra_context = {'page_title': 'Редактирование новости:'}

    def form_valid(self, form):
        form.instance.post_type = "N"
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_id', kwargs={'pk': self.object.pk})


class NewsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.post_delete',)
    model = Post
    template_name = 'news_delete.html'
    extra_context = {'page_title': 'Удаление новостей:'}
    success_url = reverse_lazy('news')

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['pk'])


class ArticleCreateView(LoginRequiredMixin, CreateView):
    raise_exception = True
    model = Post
    fields = ['title', 'content', 'categories', 'post_type', 'post_author']
    template_name = 'articles_create.html'
    extra_context = {'page_title': 'Напишите статью:'}

    def form_valid(self, form):
        form.instance.post_type = 'A'  # Устанавливаем значение поля в зависимости от страницы
        self.object = form.save(commit=False)
        self.object.post_type = form.instance.post_type
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_type'] = 'статья'  # Передача post_type в контекст шаблона
        return context


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post_a',)
    model = Post
    fields = ['title', 'content', 'categories', 'post_type']
    template_name = 'articles_create.html'
    extra_context = {'page_title': 'Редактирование статьи:'}

    def form_valid(self, form):
        # Устанавливаем значение поля post_type равным "статья"
        form.instance.post_type = "статья"
        # Сохраняем изменения
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_id', kwargs={'pk': self.object.pk})


class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post_a',)
    model = Post
    template_name = 'articles_delete.html'
    extra_context = {'page_title': 'Удаление статьи:'}
    success_url = reverse_lazy('news')

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('news')



class CategoryListView(PostsList):
    model = Post
    template_name = 'news/category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.categories = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(categories=self.categories).order_by('-created_at')
        self.filterset = PostFilter(self.request.GET, queryset=queryset)  # Создаем фильтр и сохраняем его в атрибуте класса
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.categories.subscribers.all()
        context['category'] = self.categories
        context['filterset'] = self.filterset  # Добавляем фильтр в контекст
        return context

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    msg = 'Вы успешно подписались на рассылку категории'
    return render(request, 'news/subscribe_category.html', {'category': category, 'msg': msg})


@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscription = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('category_name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscription},
    )
