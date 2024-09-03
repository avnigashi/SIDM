import os
import shutil
from image_processor import Action, log_message

class Move(Action):
    def initialize(self, params):
        self.target_dir = params.get("target_dir", "./moved_images")
        self.dry_run = params.get("dry_run", False)

    def execute(self, filepaths, metadata):
        # Since the method expects a list of file paths, we'll iterate through the list
        moved_paths = []
        for filepath in filepaths:
            print("DEBUG: Move action")
            
            # Ensure the target directory exists
            if not os.path.exists(self.target_dir):
                os.makedirs(self.target_dir)  # Correct method name
            
            target_path = os.path.join(self.target_dir, os.path.basename(filepath))
            print(f"Moving file: {filepath} to {target_path}")
    
            if self.dry_run:
                log_message(f"Dry run: {filepath} would be moved to {target_path}")
                moved_paths.append(target_path)
            else:
                try:
                    shutil.move(filepath, target_path)
                    if os.path.exists(target_path):
                        log_message(f"File successfully moved to {target_path}")
                        moved_paths.append(target_path)
                    else:
                        raise Exception(f"Failed to move {filepath} to {target_path}")
                except Exception as e:
                    log_message(f"Error: {str(e)}")
                    raise e  # Raise the exception to handle it appropriately in the process flow
        
        return moved_paths
