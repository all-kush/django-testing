import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.test.client import Client

from news.forms import BAD_WORDS
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не Автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
@pytest.mark.django_db
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
@pytest.mark.django_db
def comment(news, author):
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
    """Создаёт 10 комментариев к новости с разным временем."""
    now = timezone.now()
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'Текст {index}',
            created=now + timedelta(days=index)
        )
        for index in range(10)
    ]
    Comment.objects.bulk_create(comments)
    return Comment.objects.all()


@pytest.fixture
def id_for_args(news):
    """Возвращает кортеж с id новости."""
    return (news.id,)


@pytest.fixture
def id_for_comment_args(comment):
    """Возвращает кортеж с id комментария."""
    return (comment.id,)


@pytest.fixture
def comment_form_data():
    """Данные для формы комментария."""
    return {'text': 'Текст комментария'}


@pytest.fixture
def new_comment_data():
    """Новые данные для формы комментария."""
    return {'text': 'Обновлённый комментарий'}


@pytest.fixture
def bad_words_data():
    """Данные с нецензурными словами."""
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
