from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import localtime

from barkyapi.models import Bookmark
from barkyarch.domain.model import DomainBookmark
from barkyarch.services.commands import (
    AddBookmarkCommand,
    ListBookmarksCommand,
    DeleteBookmarkCommand,
    EditBookmarkCommand,
)


class TestCommands(TestCase):
    def setUp(self):
        right_now = localtime().date()

        self.domain_bookmark_1 = DomainBookmark(
            id=1,
            title="Test Bookmark",
            url="http://www.example.com",
            notes="Test notes",
            date_added=right_now,
        )

        self.domain_bookmark_2 = DomainBookmark(
            id=2,
            title="Test Bookmark 2",
            url="http://www.example2.com",
            notes="Test notes 2",
            date_added=right_now,
        )

    def test_command_add(self):
        add_command = AddBookmarkCommand()
        add_command.execute(self.domain_bookmark_1)

        # run checks

        # one object is inserted
        self.assertEqual(Bookmark.objects.count(), 1)

        # that object is the same as the one we inserted
        self.assertEqual(Bookmark.objects.get(id=1).url, self.domain_bookmark_1.url)

    # Added this to test listing bookmarks
    def test_command_list_default_order(self):
        add_command = AddBookmarkCommand()
        add_command.execute(self.domain_bookmark_1)
        add_command.execute(self.domain_bookmark_2)

        list_command = ListBookmarksCommand()
        result = list_command.execute()

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].id, self.domain_bookmark_1.id)
        self.assertEqual(result[1].id, self.domain_bookmark_2.id)

    # Added this to test deleting bookmarks
    def test_command_delete(self):
        add_command = AddBookmarkCommand()
        add_command.execute(self.domain_bookmark_1)

        self.assertEqual(Bookmark.objects.count(), 1)

        delete_command = DeleteBookmarkCommand()
        delete_command.execute(self.domain_bookmark_1)

        self.assertEqual(Bookmark.objects.count(), 0)

    # Added this to test editing bookmarks
    def test_command_edit(self):

        add_command = AddBookmarkCommand()
        add_command.execute(self.domain_bookmark_1)

        # using command
        # get_command = GetBookmarkCommand()
        # domain_bookmark_temp = get_command.execute(self.domain_bookmark_1.id)
        # domain_bookmark_temp.title = "Goofy"

        # or just modify
        self.domain_bookmark_1.title = "goofy"

        edit_command = EditBookmarkCommand()
        edit_command.execute(self.domain_bookmark_1)

        # run checks
        # one object is inserted
        self.assertEqual(Bookmark.objects.count(), 1)

        # that object is the same as the one we inserted
        self.assertEqual(Bookmark.objects.get(id=1).title, "goofy")