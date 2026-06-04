from http import HTTPStatus

from django.test import Client
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from .note_base import BaseNoteTest

User = get_user_model()


class TestNoteCreation(BaseNoteTest):
    """Тесты создания заметок."""
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.anonymous_client = Client()
        cls.form_data = {
            'title': 'Заголовок заметки',
            'text': 'Текст заметки',
        }
        cls.duplicate_data = {
            'title': cls.note.title,
            'text': cls.form_data['text'],
        }

    def setUp(self):
        super().setUp()
        self.initial_note_count = Note.objects.count()

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.anonymous_client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.initial_note_count)

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.initial_note_count + 1)
        note = Note.objects.last()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_cant_create_note_with_existing_slug(self):
        """Нельзя создать заметку с уже существующим slug."""
        response = self.client.post(self.add_url, data=self.duplicate_data)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.note.slug + WARNING
        )
        self.assertEqual(Note.objects.count(), self.initial_note_count)

    def test_empty_slug(self):
        """Если slug не передан, он генерируется автоматически."""
        self.client.post(self.add_url, data=self.form_data)
        note = Note.objects.last()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(BaseNoteTest):
    """Тесты редактирования и удаления заметок."""

    NEW_NOTE_TEXT = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.other_user)

        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT, }

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(Note.objects.filter(slug=self.note.slug).exists())

    def test_user_cant_delete_note_of_another_user(self):
        """Другой пользователь не может удалить чужую заметку."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(slug=self.note.slug).exists())

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Другой пользователь не может редактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.note.text)
