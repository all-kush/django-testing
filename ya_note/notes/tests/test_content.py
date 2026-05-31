from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestNoteContent(TestCase):
    """Тестирование содержимого страниц."""

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

    def test_notes_list_contains_author_note(self):
        """Список заметок автора содержит его заметку."""
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 1)
        self.assertIn(self.note, object_list)

    def test_other_user_notes_not_in_list(self):
        """В список заметок автора не попадают заметки другого пользователя."""
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.other_note, object_list)

    def test_detail_page_contains_note_content(self):
        """Страница конкретной заметки содержит заголовок и текст."""
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    def test_add_and_edit_pages_contain_form(self):
        """Страница добавления и редактирования заметки содержит форму."""
        self.client.force_login(self.author)
        pages = [
            (self.add_url, 'add'),
            (self.edit_url, 'edit'),
        ]
        for url, name in pages:
            with self.subTest(name=name):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)
