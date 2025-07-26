
class ClipboardService:
    def __init__(self, repository):
        self.repository = repository

    def poll_clipboard(self):
        # Placeholder: poll clipboard and save new entries
        pass

    def get_history(self):
        return self.repository.get_history() 