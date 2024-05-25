from django.contrib.admin import action
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import *
from django.conf import settings


@receiver(m2m_changed, sender=Post.categories.through)
def notify_about_new_post(sender, instance, action, **kwargs):
    print('**************')
    print(f' post_created called with action:{action}')
    print('**************')


@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(instance, sender, **kwargs):
    if kwargs['action'] == 'post_add':
        emails = User.objects.filter(
            subscriptions__category__in=instance.categories.all()
        ).values_list('email', flat=True)

        subject = f'Новая заметка в категории {instance.categories.all()}'

        text_content = (
            f'Тема: {instance.title}\n'
            f'Содержание: {instance.content}\n\n'
            f'Ссылка на новость: http://127.0.0.1:8000{instance.get_absolute_url()}'
        )
        html_content = (
            f'Тема: {instance.title}<br>'
            f'<a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
            f'Ссылка на заметку</a>'
        )
        for email in emails:
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

