from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from .models import Post, Subscription


@shared_task
def send_post_notification(post_id):
    post = Post.objects.get(id=post_id)
    categories = post.categories.all()
    subscribers = Subscription.objects.filter(category__in=categories).select_related('user')

    unique_subscribers = set()
    for subscription in subscribers:
        unique_subscribers.add(subscription.user)

    for subscriber in unique_subscribers:
        message = render_to_string('post_notification_email.html', {'post': post, 'subscriber': subscriber})
        send_mail(
            subject=f'New Post in {", ".join([cat.category_name for cat in categories])}: {post.title}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
        )


@shared_task
def send_weekly_newsletter():
    last_week = datetime.now() - timedelta(days=7)
    recent_posts = Post.objects.filter(created_at__gte=last_week)
    subscriptions = Subscription.objects.select_related('user', 'category')

    unique_subscribers = set()
    for subscription in subscriptions:
        unique_subscribers.add(subscription.user)

    for subscriber in unique_subscribers:
        user_subscribed_categories = subscription.categories.all()
        recent_posts_for_user = recent_posts.filter(categories__in=user_subscribed_categories).distinct()

        if recent_posts_for_user.exists():
            message = render_to_string('weekly_newsletter_email.html',
                                       {'posts': recent_posts_for_user, 'subscriber': subscriber})
            send_mail(
                subject='Weekly News Roundup',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
            )
