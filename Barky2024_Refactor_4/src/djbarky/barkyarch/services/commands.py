"""
This module utilizes the command pattern - https://en.wikipedia.org/wiki/Command_pattern - to 
specify and implement the business logic layer
"""
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from injector import Injector, inject
import pytz

import requests
from django.db import transaction

from barkyapi.models import Bookmark
from barkyarch.domain.model import DomainBookmark


class Command(ABC):
    @abstractmethod
    def execute(self, data):
        raise NotImplementedError("A command must implement the execute method")
    
class PythonTimeStampProvider:
    def __init__(self):
        self.now = datetime.now(pytz.UTC).isoformat()


class AddBookmarkCommand(Command):
    """
    Using the django orm and transactions to add a bookmark
    """

    @inject
    def __init__(self, now: PythonTimeStampProvider = PythonTimeStampProvider()):
        self.now = now

    def execute(self, data: DomainBookmark, timestamp=None):
        bookmark = Bookmark(data.id, data.title, data.url, data.notes, timestamp)
        bookmark.timestamp = self.now

        # again, we skip the ouw with django's transaction management
        with transaction.atomic():
            bookmark.save()


class GetBookmarkCommand(Command):
    """
    Using the django orm and transactions to add a bookmark
    """

    def execute(self, data: int, timestamp=None):
        return Bookmark.objects.get(id=data).to_domain()
    

class ListBookmarksCommand(Command):
    """
    swapping in Django ORM for the database manager
    """

    def __init__(self, order_by="date_added"):
        self.order_by = order_by

    def execute(self, data=None):
        return Bookmark.objects.all().order_by(self.order_by)


class DeleteBookmarkCommand(Command):
    """
    Using the django ORM to delete a bookmark
    """

    def execute(self, data: DomainBookmark):
        bookmark = Bookmark.objects.get(url=data.url)
        with transaction.atomic():
            bookmark.delete()


class EditBookmarkCommand(Command):
    """
    Using the django ORM to update a bookmark
    """

    def execute(self, data: DomainBookmark):
        bookmark = Bookmark.update_from_domain(data)
        with transaction.atomic():
            bookmark.save()
