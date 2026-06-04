from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note


User = get_user_model()


class BaseNoteTest(TestCase):
    """Базовый класс с общими данными для тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Создатель')
        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Тестовая заметка', text='Просто текст.', author=cls.author
        )
        cls.other_note = Note.objects.create(
            title='Чужая заметка', text='Чужой текст.', author=cls.other_user
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def setUp(self):
        self.client.force_login(self.author)
