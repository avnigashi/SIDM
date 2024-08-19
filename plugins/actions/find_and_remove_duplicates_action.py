import os
from typing import Dict, Any
from image_processor import Action, log_message
from PIL import Image
import imagehash
from collections import defaultdict

class FindAndRemoveDuplicatesAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.hash_size = config.get('hash_size', 8)
        self.similarity_threshold = config.get('similarity_threshold', 5)
        self.dry_run = config.get('dry_run', True)
        self.hash_dict = defaultdict(list)
        self.duplicates = []
        self.removed_files = []

        log_message(f"Initialized FindAndRemoveDuplicatesAction with hash_size: {self.hash_size}, "
                    f"similarity_threshold: {self.similarity_threshold}, dry_run: {self.dry_run}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        try:
            with Image.open(filepath) as img:
                hash = imagehash.phash(img, hash_size=self.hash_size)

            # Check for duplicates
            for existing_hash, existing_files in self.hash_dict.items():
                if abs(hash - existing_hash) <= self.similarity_threshold:
                    # Found a duplicate
                    self.duplicates.append((filepath, existing_files[0]))
                    if not self.dry_run:
                        os.remove(filepath)
                        self.removed_files.append(filepath)
                    log_message(f"{'[DRY RUN] Would remove' if self.dry_run else 'Removed'} duplicate: {filepath} (matches {existing_files[0]})")
                    return ""  # Return empty string as the file has been (or would be) removed

            # If no duplicate found, add to hash_dict
            self.hash_dict[hash].append(filepath)
            return filepath

        except Exception as e:
            error_message = f"Error processing {filepath}: {str(e)}"
            log_message(error_message)
            return filepath

    def finalize(self) -> None:
        log_message("Duplicate Images Summary:")
        for original, duplicate in self.duplicates:
            log_message(f"Original: {original}")
            log_message(f"Duplicate: {duplicate}")
            log_message(f"Action: {'Would remove (dry run)' if self.dry_run else 'Removed'}")
            log_message("")

        log_message(f"Total duplicates found: {len(self.duplicates)}")
        log_message(f"Total files {'that would be' if self.dry_run else ''} removed: {len(self.removed_files)}")