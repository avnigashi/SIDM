import os
from typing import Dict, Any
from image_processor import Action, log_message

class RemoveAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.dry_run = config.get('dry_run', False)
        log_message(f"Initialized RemoveAction with dry_run: {self.dry_run}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        if not os.path.exists(filepath):
            log_message(f"File not found: {filepath}")
            return ""

        try:
            if self.dry_run:
                log_message(f"[DRY RUN] Would remove file: {filepath}")
            else:
                os.remove(filepath)
                log_message(f"Removed file: {filepath}")

            return ""  # Return empty string as the file has been (or would be) removed
        except Exception as e:
            error_message = f"Error removing file {filepath}: {str(e)}"
            log_message(error_message)
            return filepath  # Return original filepath in case of error