import os
import shutil
from image_processor import Action, log_message

class Copy(Action):
    def initialize(self, params):
        self.target_dir = params.get("target_dir", "./copied_images")
        self.dry_run = params.get("dry_run", False)

        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

    def execute(self, filepaths, metadata):
        # Ensure filepaths is a list, even if it's a single string
        if isinstance(filepaths, str):
            filepaths = [filepaths]
        
        copied_files = []

        for filepath in filepaths:
            target_path = os.path.join(self.target_dir, os.path.basename(filepath))
            log_message(f"Copying file: {filepath} to {target_path}")

            if self.dry_run:
                log_message(f"Dry run: {filepath} would be copied to {target_path}")
                copied_files.append(filepath)
            else:
                shutil.copy(filepath, target_path)
                if os.path.exists(target_path):
                    copied_files.append(target_path)
                else:
                    log_message(f"Error copying {filepath} to {target_path}")
                    raise RuntimeError(f"Failed to copy {filepath} to {target_path}")

        return copied_files
