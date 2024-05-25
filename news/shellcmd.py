# Импортируем необходимые модели
from django.contrib.auth.models import User
from .models import Author, Category, Post, Comment
from django.db.models import Max

# Создаем двух пользователей
u1 = User.objects.create_user(username='Sergey')
u2 = User.objects.create_user(username='Yegenii')

# Создаем два объекта модели Author, связанные с пользователями
Author.objects.create(author_name=u1)
author1 = Author.objects.get(id=1)
Author.objects.create(author_name=u2)
author2 = Author.objects.get(id=2)

# Добавляем 4 категории в модель Category
Category.objects.create(category_name='Politika')
cat1 = Category.objects.get(id=1)
Category.objects.create(category_name='Ekonomika')
cat2 = Category.objects.get(id=2)
Category.objects.create(category_name='IT')
cat3 = Category.objects.get(id=3)
Category.objects.create(category_name='Sport')
cat4 = Category.objects.get(id=4)

# Добавляем 2 статьи и 1 новость
Post.objects.create(post_author=author1, post_type='A', title='Article 1', content='Content of Article 1')
post1 = Post.objects.get(id=1)
Post.objects.create(post_author=author2, post_type='A', title='Article 2', content='Content of Article 2')
post2 = Post.objects.get(id=2)
post3 = Post.objects.create(post_author=author1, post_type='N', title='News 1', content='Content of News 1')

# Присваиваем им категории
post1.categories.add(cat1, cat2)
post2.categories.add(cat3)
post3.categories.add(cat4)

# Создаем 4 комментария к разным объектам модели Post
Comment.objects.create(comment_post=Post.objects.get(id=1),comment_author=Author.objects.get(id=1).author_name, text='Комментарий1')
comment1 = Comment.objects.get(id=1)
Comment.objects.create(comment_post=Post.objects.get(id=1),comment_author=u2, text='Комментарий2')
comment2 = Comment.objects.get(id=2)
comment3 = Comment.objects.create(comment_post=post2, comment_author=u1, text='Комментарий3')
comment4 = Comment.objects.create(comment_post=post3, comment_author=u2, text='Комментарий4')

# Применяем функции like() и dislike() к статьям/новостям и комментариям
post1.like()
post2.dislike()
comment1.like()
post1.like()
post1.dislike()
comment1.like()
comment2.dislike()
comment3.like()
comment3.like()
comment4.dislike()

# Обновляем рейтинги пользователей
author1.generate()
author2.generate()

# Выводим username и рейтинг лучшего пользователя
ba_rating = Author.objects.aggregate(max_rating=Max('author_rating'))
print(f'{ba_rating}')

best_author = Author.objects.order_by('-author_rating')[:1]
if best_author:
    username = best_author[0].author_name.username
    print(f'Best user: {username}, with rating: {best_author[0].author_rating}')
else:
    print("No authors found.")


# Выводим дату добавления, username автора, рейтинг, заголовок и превью лучшей статьи
best_post = Post.objects.order_by('-author_rating').first()
print(f' Better post was added:{best_post.created_at}, Name of Author:{best_post.post_author},'
      f' Total Rating:{best_post.post_rating}, Title:{best_post.title}. Short preview: {best_post.preview()}')

# Выводим все комментарии (дата, пользователь, рейтинг, текст) к этой статье
comments = Comment.objects.filter(comment_post=best_post)
for comment in comments:
    print(f"Date: {comment.created_at}, User: {comment.comment_author.username}, Rating: {comment.comment_rating}, Text: {comment.text}")

