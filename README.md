# Smart Image Dataset Manager (SIDM)

SIDM is a flexible and powerful tool for managing and processing image datasets. It provides a modular framework for applying various rules and actions to images, making it ideal for tasks such as dataset preparation, face detection, attribute analysis, and privacy protection.

## Features

- Modular plugin-based architecture for rules and actions
- Configurable processes via YAML configuration file
- Support for various image processing tasks:
   - Face detection and recognition using DeepFace
   - Facial attribute analysis (age, gender, race, emotion)
   - Anti-spoofing detection
   - Face blurring for privacy protection
   - Custom rules and actions support
- Flexible workflow creation by combining different rules and actions

## Prerequisites

- Python 3.7+
- DeepFace library
- OpenCV
- PyYAML

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/avnigashi/SIDM.git
   cd SIDM
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

The behavior of SIDM is controlled by the `sidm_config.yaml` file. This file defines the processes, rules, and actions to be applied to the images.

Example configuration:

```yaml
general:
  output_dir: "./processed_dataset"
  log_level: "INFO"
  plugins_dir: "./plugins"
  recursive: true
  stop_on_error: false

processes:
  face_blurring:
    rules:
      - name: is_image
        file: is_image.py
        params:
          allowed_formats:
            - ".jpg"
            - ".jpeg"
            - ".png"
    actions:
      - name: detect_and_blur_faces
        file: detect_and_blur_faces.py
        params:
          detector_backend: "retinaface"
          blur_factor: 31
          output_dir: "./blurred_faces"
        conditions:
          - is_image
```

## Usage

To run SIDM, use the following command:

```
python main.py <process_name> <input_directory> [--config <config_file>]
```

For example:

```
python main.py face_blurring ./my_images
```

This will apply the `face_blurring` process to all images in the `./my_images` directory.

## Adding Custom Rules and Actions

1. Create a new Python file in the appropriate plugin directory (`plugins/rules/` or `plugins/actions/`).
2. Define a class that inherits from `Rule` or `Action`.
3. Implement the required methods (`initialize` and `apply` for rules, `initialize` and `execute` for actions).
4. Add the new rule or action to your `sidm_config.yaml` file.

Example custom rule:

```python
from typing import Dict, Any
from image_processor import Rule, log_message

class MyCustomRule(Rule):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.my_param = config.get('my_param', 'default_value')
        log_message(f"Initialized MyCustomRule with my_param: {self.my_param}")

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        # Implement your rule logic here
        return True
```

## Available Rules and Actions

SIDM comes with several pre-implemented rules and actions:

### Rules:
- `is_image`: Checks if a file is a valid image format
- `age_rule`: Filters images based on detected face age
- `gender_rule`: Filters images based on detected face gender
- `race_rule`: Filters images based on detected face race
- `emotion_rule`: Filters images based on detected face emotion
- `spoofing_rule`: Detects potential image spoofing
- etc

### Actions:
- `copy_file`: Copies matching images to an output directory
- `crop_faces`: Detects and crops faces from images
- `detect_and_blur_faces`: Detects faces and applies a blur effect
- etc

