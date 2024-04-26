from datetime import date


class DomainBookmark:
    """
    Bookmark domain model. Note, this is much simpler than P&G's domain model.
    """

    def __init__(self, id, title, url, notes, date_added):
        self.id = id
        self.title = title
        self.url = url
        self.notes = notes
        self.date_added = date_added

    def __str__(self):
        return f"{self.title}"
