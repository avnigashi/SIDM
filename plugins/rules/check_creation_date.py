import os
from datetime import datetime, timedelta
from typing import Dict, Any
from image_processor import Rule, log_message

class CheckCreationDate(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.max_age_days = config['max_age_days']
        log_message(f"Initialized CheckCreationDate with max age: {self.max_age_days} days")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        creation_time = datetime.fromtimestamp(os.path.getctime(filepath))
        age = datetime.now() - creation_time
        result = age <= timedelta(days=self.max_age_days)
        log_message(f"CheckCreationDate: {filepath} (Age: {age.days} days) - {'Passed' if result else 'Failed'}")
        return result