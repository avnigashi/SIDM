import os
from image_processor import Rule  # Ensure Rule is imported

class FileType(Rule):  # Inherit from Rule
    def initialize(self, params):
        self.allowed_types = params.get("allowed_types", [".txt", ".pdf", ".docx", ".xlsx"])

    def apply(self, filepath, metadata):
        file_extension = os.path.splitext(filepath)[1].lower()
        is_allowed = file_extension in self.allowed_types
        print(f"Checking file type for {filepath}: {file_extension} is {'allowed' if is_allowed else 'not allowed'}")
        return is_allowed
