from notes.forms import NoteForm
from .note_base import BaseNoteTest


class TestNoteContent(BaseNoteTest):
    """Тестирование содержимого страниц."""

    def test_notes_list_contains_author_note(self):
        """Список заметок автора содержит его заметку."""
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 1)
        self.assertIn(self.note, object_list)

    def test_other_user_notes_not_in_list(self):
        """В список заметок автора не попадают заметки другого пользователя."""
        response = self.client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertNotIn(self.other_note, object_list)

    def test_detail_page_contains_note_content(self):
        """Страница конкретной заметки содержит заголовок и текст."""
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    def test_add_and_edit_pages_contain_form(self):
        """Страница добавления и редактирования заметки содержит форму."""
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
