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
from channels.testing import ApplicationCommunicator
from channels.layers import get_channel_layer
from barkyapi.signals import send_bookmark_to_channel, log_bookmark_to_csv
import os
import csv
from unittest.mock import patch

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


# testing logging bookmarks to csv
class SignalHandlersTestCase(TestCase):
    def setUp(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # Create a test CSV file path
        self.csv_file_path = os.path.join(current_directory, "domain", "created_log.csv")
        self.channel_layer = get_channel_layer()

    def tearDown(self):
        # Remove the test CSV file after the test is done
        if os.path.exists(self.csv_file_path):
            os.remove(self.csv_file_path)

    def test_log_bookmark_to_csv(self):
        # Create a mock Bookmark instance
        bookmark = Bookmark.objects.create(
            title="Test Bookmark",
            url="http://www.example.com",
            notes="Test notes",
            date_added=localtime().date()
        )

        # Call the signal handler
        log_bookmark_to_csv(sender=Bookmark, instance=bookmark)

        # Check if the CSV file was created
        self.assertTrue(os.path.exists(self.csv_file_path))

        # Read the content of the CSV file
        with open(self.csv_file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            rows = list(csv_reader)

            # Check if the CSV file contains the expected data
            self.assertEqual(rows[1][1], "Test Bookmark")  # Title
            self.assertEqual(rows[1][2], "http://www.example.com")  # URL
            self.assertEqual(rows[1][3], "Test notes")  # Notes

    def test_send_bookmark_to_channel(self):
        # Create a mock Bookmark instance
        bookmark = Bookmark.objects.create(
            title="Test Bookmark",
            url="http://www.example.com",
            notes="Test notes",
            date_added=localtime().date()
        )

        class MockChannelLayer:
            def send(self, *args, **kwargs):
                pass

        mock_channel_layer = MockChannelLayer()

        # Patch the channel layer
        with patch("barkyapi.signals.get_channel_layer", return_value=mock_channel_layer):
            # Call the signal handler
            send_bookmark_to_channel(sender=Bookmark, instance=bookmark)