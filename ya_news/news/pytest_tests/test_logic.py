from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, id_for_args,
                                            comment_form_data,
                                            initial_comments_count):
    """Анонимный пользователь не может создать комментарий."""
    url = reverse('news:detail', args=id_for_args)
    client.post(url, data=comment_form_data)
    assert Comment.objects.count() == initial_comments_count


def test_user_can_create_comment(author_client, news,
                                 id_for_args, comment_form_data,
                                 author, initial_comments_count):
    """Авторизованный пользователь может создать комментарий."""
    url = reverse('news:detail', args=id_for_args)
    response = author_client.post(url, data=comment_form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == initial_comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
        'bad_word', BAD_WORDS)
def test_user_cant_use_bad_words(author_client, id_for_args,
                                 bad_word, initial_comments_count):
    """При попытке добавить bad word форма возвращает ошибку."""
    url = reverse('news:detail', args=id_for_args)
    bad_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = author_client.post(url, data=bad_data)
    form = response.context['form']
    assertFormError(form, field='text', errors=WARNING)
    assert Comment.objects.count() == initial_comments_count


def test_author_can_delete_comment(author_client,
                                   id_for_args, id_for_comment_args):
    """Автор может удалить свой комментарий."""
    delete_url = reverse('news:delete', args=id_for_comment_args)
    url_to_comments = reverse('news:detail', args=id_for_args) + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert not Comment.objects.filter(id=id_for_comment_args[0]).exists()


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  id_for_comment_args):
    """Пользователь не может удалить чужой комментарий."""
    delete_url = reverse('news:delete', args=id_for_comment_args)
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=id_for_comment_args[0]).exists()


def test_author_can_edit_comment(author, news, author_client, comment,
                                 new_comment_data,
                                 id_for_args, id_for_comment_args):
    """Автор может редактировать свой комментарий."""
    edit_url = reverse('news:edit', args=id_for_comment_args)
    url_to_comments = reverse('news:detail', args=id_for_args) + '#comments'
    response = author_client.post(edit_url, data=new_comment_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_comment_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(not_author_client, comment,
                                                new_comment_data,
                                                id_for_comment_args):
    """Пользователь не может редактировать чужой комментарий."""
    edit_url = reverse('news:edit', args=id_for_comment_args)
    response = not_author_client.post(edit_url, data=new_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != new_comment_data['text']
