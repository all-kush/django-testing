from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, detail_url,
                                            comment_form_data,
                                            initial_comments_count):
    """Анонимный пользователь не может создать комментарий."""
    client.post(detail_url, data=comment_form_data)
    assert Comment.objects.count() == initial_comments_count


def test_user_can_create_comment(author_client, news,
                                 comment_form_data, detail_url,
                                 author, initial_comments_count):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=comment_form_data)
    expected_url = f'{detail_url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, detail_url,
                                 bad_word, initial_comments_count):
    """При попытке добавить bad word форма возвращает ошибку."""
    bad_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(detail_url, data=bad_data)
    form = response.context['form']
    assertFormError(form, field='text', errors=WARNING)
    assert Comment.objects.count() == initial_comments_count


def test_author_can_delete_comment(author_client,
                                   news, comment, delete_url):
    """Автор может удалить свой комментарий."""
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  comment, delete_url):
    """Пользователь не может удалить чужой комментарий."""
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id).exists()


def test_author_can_edit_comment(author, news, author_client, comment,
                                 new_comment_data, edit_url, detail_url):
    """Автор может редактировать свой комментарий."""
    url_to_comments = detail_url + '#comments'
    before_edit_created = comment.created
    response = author_client.post(edit_url, data=new_comment_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_comment_data['text']
    assert comment.author == author
    assert comment.news == news
    assert comment.created == before_edit_created


def test_user_cant_edit_comment_of_another_user(not_author_client, comment,
                                                new_comment_data,
                                                edit_url, news, author):
    """Пользователь не может редактировать чужой комментарий."""
    before_edit_created = comment.created
    before_edit_text = comment.text
    response = not_author_client.post(edit_url, data=new_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != new_comment_data['text']
    assert comment.text == before_edit_text
    assert comment.author == author
    assert comment.news == news
    assert comment.created == before_edit_created
