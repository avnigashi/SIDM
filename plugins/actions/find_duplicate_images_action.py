import os
from typing import Dict, Any, List
from image_processor import Action, log_message
from PIL import Image
import imagehash
from collections import defaultdict

class FindDuplicateImagesAction(Action):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.output_dir = config.get('output_dir', 'duplicate_images')
        self.hash_size = config.get('hash_size', 8)
        self.similarity_threshold = config.get('similarity_threshold', 5)
        self.hash_dict = defaultdict(list)
        self.duplicates = []

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        log_message(f"Initialized FindDuplicateImagesAction with hash_size: {self.hash_size}, "
                    f"similarity_threshold: {self.similarity_threshold}, output_dir: {self.output_dir}")

    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
        try:
            with Image.open(filepath) as img:
                hash = imagehash.phash(img, hash_size=self.hash_size)

            # Check for duplicates
            for existing_hash, existing_files in self.hash_dict.items():
                if abs(hash - existing_hash) <= self.similarity_threshold:
                    self.duplicates.append((filepath, existing_files[0]))
                    log_message(f"Found duplicate: {filepath} matches {existing_files[0]}")
                    return filepath  # Return early as we've found a duplicate

            # If no duplicate found, add to hash_dict
            self.hash_dict[hash].append(filepath)

            return filepath

        except Exception as e:
            error_message = f"Error processing {filepath}: {str(e)}"
            log_message(error_message)
            return filepath

    def finalize(self) -> None:
        # Write duplicates to a file
        output_file = os.path.join(self.output_dir, 'duplicate_images.txt')
        with open(output_file, 'w') as f:
            for original, duplicate in self.duplicates:
                f.write(f"Original: {original}\nDuplicate: {duplicate}\n\n")

        log_message(f"Found {len(self.duplicates)} sets of duplicate images. "
                    f"Results written to {output_file}")

    def get_duplicates(self) -> List[tuple]:
        return self.duplicates