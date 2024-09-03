# Smart Image Dataset Manager

The Smart Image Dataset Manager (SIDM) is a flexible tool designed to manage and process large image datasets. It leverages a plugin-based system where users can define custom rules and actions to tailor the image processing pipeline according to their needs.

## Features

- **Customizable Processing Pipelines**: Define your own rules and actions using plugins.
- **Plugin System**: Easily extend functionality by adding new rules and actions.
- **Configurable via YAML**: Manage processes and settings through a simple YAML configuration file.
- **Error Handling & Logging**: Optional detailed logging and error management.

## Installation

Ensure you have Python 3.7+ installed. Install the required dependencies:

```bash
pip install -r requirements.txt
```

If you use plugins with additional dependencies, install them by running:

```bash
python main.py --install
```

This command searches for `requirements.txt` files in the `plugins` directory and installs any necessary packages.

## Usage

Run the tool using the following command:

```bash
python main.py <process_name> [source_dir] [options]
```

- `process_name`: The name of the process to run (as defined in the YAML config).
- `source_dir`: (Optional) Directory containing images to process.

### Options

- `-c`, `--config`: Path to the configuration file (default: `sidm_config.yaml`).
- `--stop-on-error`: Stop processing on the first error encountered.
- `--log`: Enable detailed logging.
- `--install`: Install plugin requirements.

### Example

```bash
python main.py process_images ./images --log
```

This command processes images in the `./images` directory using the `process_images` pipeline.

## Configuration

The configuration is managed via `sidm_config.yaml`. Example structure:

```yaml
general:
  log_level: INFO
  plugins_dir: ./plugins
  stop_on_error: false

processes:
  process_images:
    rules:
      - plugin: custom_plugin/custom_rule
        name: file_size_check
        params:
          threshold: 500000
    actions:
      - plugin: custom_plugin/custom_action
        name: copy_files
        params:
          output_dir: ./output
        conditions:
          - file_size_check
```

## Plugin System

### Structure

Plugins are organized within the `plugins` directory:

```
plugins/
├── custom_plugin/
│   ├── rules/
│   │   └── custom_rule.py
│   └── actions/
│       └── custom_action.py
```

### Creating Plugins

1. **Rule Plugin**: Inherit from `Rule` and implement `initialize` and `apply`.
2. **Action Plugin**: Inherit from `Action` and implement `initialize` and `execute`.

Example of a rule plugin (`custom_rule.py`):

```python
from image_processor import Rule

class CustomRule(Rule):
    def initialize(self, config):
        self.threshold = config.get('threshold', 100)

    def apply(self, filepath, metadata):
        return metadata['size'] < self.threshold
```

Example of an action plugin (`custom_action.py`):

```python
from image_processor import Action

class CustomAction(Action):
    def initialize(self, config):
        self.output_dir = config.get('output_dir', './processed')

    def execute(self, filepaths, metadata):
        processed_files = []
        for filepath in filepaths:
            new_path = os.path.join(self.output_dir, os.path.basename(filepath))
            shutil.copy(filepath, new_path)
            processed_files.append(new_path)
        return processed_files
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
