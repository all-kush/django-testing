from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args',
    [
        ('news:home', None),
        ('users:login', None),
        ('users:signup', None),
        ('news:detail', lf('id_for_args')),
    ]
)
def test_pages_availability(client, name, args):
    """Страницы, доступные всем."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (lf('author_client'), HTTPStatus.OK),
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
    ]
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'))
def test_edit_delete_pages_availability(parametrized_client, name,
                                        expected_status, comment):
    """Доступность страниц редактирования/удаления для разных пользователей."""
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_redirect_for_anonymous(client, name, comment):
    """Перенаправление анонимного пользователя."""
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
