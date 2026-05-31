from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    """Тесты маршрутов."""

    ROUTES = [
        ('notes:edit', True),
        ('notes:delete', True),
        ('notes:detail', True),
        ('notes:list', False),
        ('notes:add', False),
        ('notes:success', False),]

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
            )

    def test_pages_availability(self):
        """Страницы, доступные всем пользователям."""
        urls = ('notes:home', 'users:login', 'users:signup', 'users:logout')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                if name == 'users:logout':
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_author(self):
        """Автор имеет доступ ко всем страницам."""
        self.client.force_login(self.author)
        for name, need_slug in self.ROUTES:
            with self.subTest(name=name):
                if need_slug:
                    url = reverse(name, args=(self.note.slug,))
                else:
                    url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_another_user_cannot_access_note(self):
        """У другого пользователя нет доступа к detail, edit, delete."""
        self.client.force_login(self.other_user)
        urls = ('notes:detail', 'notes:edit', 'notes:delete')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """Переадресация анонимного пользователя."""
        login_url = reverse('users:login')

        for name, need_slug in self.ROUTES:
            with self.subTest(name=name):
                if need_slug:
                    url = reverse(name, args=(self.note.slug,))
                else:
                    url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
