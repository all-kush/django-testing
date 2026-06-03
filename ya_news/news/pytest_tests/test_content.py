import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, news_ten_plus_one, home_url):
    """На главной странице отображается NEWS_COUNT_ON_HOME_PAGE новостей."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_ten_plus_one, home_url):
    """На главной странице новости отсортированы: сначала новые."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, comments, detail_url):
    """На странице новости отсортированы: сначала старые."""
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):
    """Анонимный пользователь не видит форму добавления комментария."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    """Авторизованный пользователь видит форму комментария(CommentForm)."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
