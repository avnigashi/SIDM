import argparse
import yaml
from image_processor import ImageProcessor, log_message

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    log_message(f"Configuration loaded from {config_file}")
    return config

def main():
    parser = argparse.ArgumentParser(description="Smart Image Dataset Manager")
    parser.add_argument("process", help="Name of the process to run")
    parser.add_argument("source_dir", help="Directory containing images to process")
    parser.add_argument("-c", "--config", default="sidm_config.yaml", help="Path to configuration file")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop processing if an error occurs")
    args = parser.parse_args()

    log_message(f"Selected process: {args.process}")
    log_message(f"Processing directory: {args.source_dir}")
    log_message(f"Using config file: {args.config}")
    log_message(f"Stop on error: {args.stop_on_error}")

    config = load_config(args.config)

    # Override the stop_on_error setting from command line if provided
    if args.stop_on_error:
        config['general']['stop_on_error'] = True
        log_message("logging enabled")

    if args.process not in config['processes']:
        print(f"Error: Process '{args.process}' not found in configuration.")
        return

    processor = ImageProcessor(config)
    processor.load_plugins()
    processor.process_images(args.source_dir, args.process)

    log_message("Image processing completed")

    # Print the log
    print("\nProcessing Log:")
    for log_entry in processor.get_log():
        print(log_entry)

if __name__ == "__main__":
    main()