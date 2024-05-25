import logging

from django import forms
from django.core.exceptions import ValidationError
from .models import Post
from .resources import POST_TYPE_CHOICES

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PostForm(forms.ModelForm):
    title = forms.CharField(min_length=10, label='Заголовок')
    content = forms.CharField(min_length=50, widget=forms.Textarea)
    # post_type = forms.CharField(max_length=15, label='Укажите тип')
    # categories = forms.MultipleChoiceField(max_length=15, label='Выберите категорию')
    post_type = forms.ChoiceField(label='Тип поста', choices=POST_TYPE_CHOICES)

    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'categories',
            'post_type',
            'post_author'
        ]

    def clean_content(self):
        # cleaned_data = super().clean()
        title = self.cleaned_data.get("title")
        content = self.cleaned_data.get("content")

        if content is not None and len(content.strip()) == 0:
            raise ValidationError("Содержание не может быть пустым.")

        if content is not None and len(content) < 10:
            raise ValidationError("Содержание не может быть менее 10 символов.")

        if title == content:
            raise ValidationError("Содержание не может быть идентично названию.")

        return content

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title[0].islower():
            raise ValidationError(
                "Название должно начинаться с заглавной буквы"
            )
        return title

    def save(self, commit=True):
        instance = super(PostForm, self).save(commit=False)
        post_type_str = self.cleaned_data.get('post_type')
        logger.debug(f"Value of post_type: {post_type_str}")

        # Получаем соответствующий ключ для выбранного значения post_type
        post_type_key = dict(POST_TYPE_CHOICES).get(post_type_str)
        instance.post_type = post_type_key

        if commit:
            instance.save()
        return instance
