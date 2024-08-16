import os
import logging
import importlib.util
from typing import Dict, List, Any
from abc import ABC, abstractmethod

global_log = []

def log_message(message: str):
    global_log.append(message)

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
    def execute(self, filepath: str, metadata: Dict[str, Any]) -> str:
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

    def execute(self, filepath: str, metadata: Dict[str, Any], rule_results: Dict[str, bool]) -> str:
        current_filepath = filepath
        for action in self.actions:
            conditions = action['config'].get('conditions', [])
            if all(rule_results.get(condition, False) for condition in conditions):
                try:
                    current_filepath = action['instance'].execute(current_filepath, metadata)
                except Exception as e:
                    log_message(f"Error executing action {action['config']['name']} on {current_filepath}: {str(e)}")
            else:
                log_message(f"Skipped action {action['config']['name']} for {current_filepath} due to unmet conditions")
        return current_filepath

class ImageProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.process: Process = None
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

        for rule_config in process_config['rules']:
            rule_path = os.path.join(plugin_dir, 'rules', rule_config['file'])
            rule = PluginLoader.load_plugin(rule_path, Rule)
            rule.initialize(rule_config.get('params', {}))
            rules.append({'instance': rule, 'config': rule_config})

        for action_config in process_config['actions']:
            action_path = os.path.join(plugin_dir, 'actions', action_config['file'])
            action = PluginLoader.load_plugin(action_path, Action)
            action.initialize(action_config.get('params', {}))
            actions.append({'instance': action, 'config': action_config})

        self.process = Process(process_name, rules, actions)
        log_message(f"Loaded process: {process_name}")

    def process_images(self, source_dir: str):
        if not self.process:
            raise ValueError("No process loaded. Call load_plugins() first.")

        for root, _, files in os.walk(source_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    metadata = self._get_metadata(filepath)
                    rule_results = self.process.apply(filepath, metadata)
                    if any(rule_results.values()):
                        filepath = self.process.execute(filepath, metadata, rule_results)
                        self.logger.info(f"Applied process '{self.process.name}' to {filepath}")
                        log_message(f"Applied process '{self.process.name}' to {filepath}")
                    else:
                        log_message(f"Skipped process '{self.process.name}' for {filepath}")
                except Exception as e:
                    self.logger.error(f"Error processing {filepath}: {str(e)}")
                    log_message(f"Error processing {filepath}: {str(e)}")
                    if self.config['general']['stop_on_error']:
                        raise

            if not self.config['general']['recursive']:
                break

    def _get_metadata(self, filepath: str) -> Dict[str, Any]:
        return {
            'filename': os.path.basename(filepath),
            'size': os.path.getsize(filepath),
        }

    def get_log(self) -> List[str]:
        return global_log