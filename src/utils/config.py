import yaml

def load_config(config_path: str) -> dict:
    """Загружает конфигурацию из YAML-файла."""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)