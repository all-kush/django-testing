import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    """Возвращает объект пользователя являющегося автором."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Возвращает объект пользователя, не являющегося автором."""
    return django_user_model.objects.create(username='Не Автор')


@pytest.fixture
def author_client(author):
    """Возвращает авторизованный клиент для автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Возвращает авторизованный клиент для не автора."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
@pytest.mark.django_db
def news():
    """Возвращает объект новости."""
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
@pytest.mark.django_db
def comment(news, author):
    """Возвращает объект комментария к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
@pytest.mark.django_db
def news_ten_plus_one():
    """Создаёт NEWS_COUNT_ON_HOME_PAGE + 1 новостей с разными датами."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)]
    News.objects.bulk_create(all_news)
    return News.objects.all()


@pytest.fixture
@pytest.mark.django_db
def comments(news, author):
    """Создаёт COMMENTS_COUNT комментариев к новости с разным временем."""
    now = timezone.now()
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'Текст {index}',
            created=now + timedelta(days=index)
        )
        for index in range(settings.COMMENTS_COUNT)
    ]
    Comment.objects.bulk_create(comments)
    return Comment.objects.all()


@pytest.fixture
def comment_form_data():
    """Данные для формы комментария."""
    return {'text': 'Текст комментария'}


@pytest.fixture
def new_comment_data():
    """Новые данные для формы комментария."""
    return {'text': 'Обновлённый комментарий'}


@pytest.fixture
def id_for_args(news):
    """Возвращает кортеж с id новости."""
    return (news.id,)


@pytest.fixture
def home_url():
    """Возвращает URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    """Возвращает URL страницы отдельной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    """Возвращает URL редактирования комментария."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    """Возвращает URL страницы удаления комментария."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def initial_comments_count():
    """Возвращает начальное количество комментариев в БД."""
    return Comment.objects.count()
