import argparse
import yaml
from image_processor import ImageProcessor, set_logging
import os
import subprocess
import sys

def install_plugin_requirements(plugins_dir):
    for root, dirs, files in os.walk(plugins_dir):
        if 'requirements.txt' in files:
            requirements_path = os.path.join(root, 'requirements.txt')
            install_requirements(requirements_path)

def install_requirements(requirements_path):
    try:
        # Use subprocess to run pip install
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_path])
        print(f"Installed requirements from {requirements_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements from {requirements_path}: {str(e)}")

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Smart Image Dataset Manager")
    parser.add_argument("process", help="Name of the process to run")
    parser.add_argument("source_dir", nargs='?', default=None, help="Directory containing images to process (optional)")
    parser.add_argument("-c", "--config", default="sidm_config.yaml", help="Path to configuration file")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop processing if an error occurs")
    parser.add_argument("--log", action="store_true", help="Enable detailed logging")
    parser.add_argument("--install", action="store_true", help="Install plugin requirements")
    args = parser.parse_args()

    # Conditionally install plugin requirements
    if args.install:
        plugins_dir = "./plugins"
        install_plugin_requirements(plugins_dir)

    set_logging(args.log)

    config = load_config(args.config)

    if args.stop_on_error:
        config['general']['stop_on_error'] = True

    processor = ImageProcessor(config)
    processor.load_plugins(args.process)

    if args.source_dir:
        print(f"Processing images in directory: {args.source_dir}")
        processor.process_images(args.source_dir)
    else:
        print("No source directory provided. Executing action directly.")
        # Directly invoke the first action if no source directory is provided
        for action in processor.processes[args.process].actions:
            generated_image_path = action['instance'].execute()
            print(f"Generated image saved at: {generated_image_path}")

    if args.log:
        print("\nProcessing Log:")
        for log_entry in processor.get_log():
            print(log_entry)

if __name__ == "__main__":
    main()
