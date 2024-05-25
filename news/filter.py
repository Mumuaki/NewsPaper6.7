from django_filters import FilterSet, DateTimeFilter, CharFilter, ChoiceFilter
from django.forms.widgets import DateTimeInput
from .models import Post
from .resources import POST_TYPE_CHOICES


class NewsFilter(FilterSet):
    class Meta:
        model = Post
        fields = ['categories', 'created_at']


class PostFilter(FilterSet):
    added_after = DateTimeFilter(
        field_name='created_at',
        lookup_expr='gt',
        label='Добавлено после',
        widget=DateTimeInput(
            format='%d-%m-%Y',
            attrs={'type': 'datetime-local'},
        ),
    )
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label='Название содержит',
    )

    post_type = ChoiceFilter(
        label='Категория поста',
        empty_label='Выбери из списка',
        choices=[(choice[0], choice[1]) for choice in POST_TYPE_CHOICES],  # Используем значения из POST_TYPE_CHOICES
        field_name='post_type',
        lookup_expr='exact',
    )

    class Meta:
        model = Post
        fields = ['added_after', 'title', 'categories', 'post_type']
