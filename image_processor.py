import os
import logging
import importlib.util
from typing import Dict, List, Any
from abc import ABC, abstractmethod
from tqdm import tqdm

global_log = []
logging_enabled = False

def set_logging(enabled: bool):
    global logging_enabled
    logging_enabled = enabled

def log_message(message: str):
    global_log.append(message)
    if logging_enabled:
        print(message)

class Plugin(ABC):
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        pass

class Rule(Plugin):
    @abstractmethod
    def apply(self, filepath: str, metadata: Dict[str, Any]) -> bool:
        pass

class Action(Plugin):
    @abstractmethod
    def execute(self, filepaths: List[str], metadata: Dict[str, Any]) -> List[str]:
        pass

class PluginLoader:
    @staticmethod
    def load_plugin(plugin_file: str, base_class: type) -> Plugin:
        spec = importlib.util.spec_from_file_location("plugin", plugin_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for item in dir(module):
            obj = getattr(module, item)
            if isinstance(obj, type) and issubclass(obj, base_class) and obj != base_class:
                return obj()
        raise ValueError(f"No valid plugin found in {plugin_file}")

class Process:
    def __init__(self, name: str, rules: List[Dict[str, Any]], actions: List[Dict[str, Any]]):
        self.name = name
        self.rules = rules
        self.actions = actions

    def apply(self, filepath: str, metadata: Dict[str, Any]) -> Dict[str, bool]:
        results = {}
        for rule in self.rules:
            rule_name = rule['config']['name']
            try:
                results[rule_name] = rule['instance'].apply(filepath, metadata)
            except Exception as e:
                log_message(f"Error applying rule {rule_name} to {filepath}: {str(e)}")
                results[rule_name] = False
        return results

    def execute(self, filepaths: List[str], metadata: Dict[str, Any], rule_results: Dict[str, bool]) -> List[str]:
        current_filepaths = filepaths
        for action in self.actions:
            conditions = action['config'].get('conditions', [])
            if all(rule_results.get(condition, False) for condition in conditions):
                try:
                    current_filepaths = action['instance'].execute(current_filepaths, metadata)
                    log_message(f"Executed action {action['config']['name']} on {current_filepaths}")
                except Exception as e:
                    raise RuntimeError(f"Error executing action {action['config']['name']}: {str(e)}") from e
            else:
                log_message(f"Skipped action {action['config']['name']} due to unmet conditions: {conditions}")
        return current_filepaths

class ImageProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.processes: Dict[str, Process] = {}
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger('ImageProcessor')
        logger.setLevel(self.config['general']['log_level'])
        handler = logging.FileHandler('image_processor.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def load_plugins(self, process_name: str):
        if process_name not in self.config['processes']:
            raise ValueError(f"Process '{process_name}' not found in configuration")

        process_config = self.config['processes'][process_name]
        plugin_dir = self.config['general']['plugins_dir']

        rules = []
        actions = []

        if 'rules' in process_config:
            for rule_config in process_config['rules']:
                rule_name = rule_config['plugin'].split("/")[-1].split(".")[0]
                rule_config['name'] = rule_config.get('name', rule_name)
                rule_path = os.path.abspath(os.path.join(plugin_dir, rule_config['plugin'].split('/')[0], 'rules', *rule_config['plugin'].split('/')[1:]) + ".py")
                rule = PluginLoader.load_plugin(rule_path, Rule)
                rule.initialize(rule_config.get('params', {}))
                rules.append({'instance': rule, 'config': rule_config})

        if 'actions' in process_config:
            for action_config in process_config['actions']:
                action_name = action_config['plugin'].split("/")[-1].split(".")[0]
                action_config['name'] = action_config.get('name', action_name)
                action_path = os.path.abspath(os.path.join(plugin_dir, action_config['plugin'].split('/')[0], 'actions', *action_config['plugin'].split('/')[1:]) + ".py")
                action = PluginLoader.load_plugin(action_path, Action)
                action.initialize(action_config.get('params', {}))
                actions.append({'instance': action, 'config': action_config})

        self.processes[process_name] = Process(process_name, rules, actions)

    def process_images(self, source_dir: str):
        all_files = []
        for root, _, files in os.walk(source_dir):
            for filename in files:
                all_files.append(os.path.join(root, filename))

        log_message(f"Found {len(all_files)} files in total.")

        image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        log_message(f"Identified {len(image_files)} image files.")

        with tqdm(total=len(image_files), desc="Processing Images", unit="image") as pbar:
            for filepath in image_files:
                log_message(f"Processing file: {filepath}")
                try:
                    metadata = self._get_metadata(filepath)
                    for process_name, process in self.processes.items():
                        log_message(f"Applying process '{process_name}' to {filepath}")
                        rule_results = process.apply(filepath, metadata)
                        log_message(f"Rule results for {filepath}: {rule_results}")
                        if any(rule_results.values()):
                            filepath = process.execute([filepath], metadata, rule_results)[0]
                            self.logger.info(f"Applied process '{process_name}' to {filepath}")
                            log_message(f"Applied process '{process_name}' to {filepath}")
                        else:
                            log_message(f"Skipped process '{process_name}' for {filepath}")
                except Exception as e:
                    error_message = f"Error processing {filepath}: {str(e)}"
                    self.logger.error(error_message)
                    log_message(error_message)
                    if self.config['general'].get('stop_on_error', False):
                        raise RuntimeError("Critical error occurred. Stopping the process.") from e
                finally:
                    pbar.update(1)

        log_message("Image processing completed.")

    def _get_metadata(self, filepath: str) -> Dict[str, Any]:
        return {
            'filename': os.path.basename(filepath),
            'size': os.path.getsize(filepath),
        }

    def get_log(self) -> List[str]:
        return global_log
