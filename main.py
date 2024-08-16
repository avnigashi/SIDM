import argparse
import yaml
from image_processor import ImageProcessor, log_message

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

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

    if args.stop_on_error:
        config['general']['stop_on_error'] = True

    processor = ImageProcessor(config)
    processor.load_plugins(args.process)
    processor.process_images(args.source_dir)

    log_message("Image processing completed")

    print("\nProcessing Log:")
    for log_entry in processor.get_log():
        print(log_entry)

if __name__ == "__main__":
    main()