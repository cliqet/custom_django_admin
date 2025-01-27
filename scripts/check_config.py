import os
from pathlib import Path

import toml

"""
    Script to check whether config.toml file has all the environment variables
    required by template.config.toml.
    Prints out the missing environment variables
    To run in the root directory, run python ./scripts/check_config.py
    within virtual environment
"""

def traverse_dict_keys(d, parent=None):
    keys_list = []

    for key, value in d.items():
        current_key = key if parent is None else f"{parent}:{key}"
        keys_list.append(current_key)

        if isinstance(value, dict):
            nested_keys = traverse_dict_keys(value, parent=current_key)
            keys_list.extend(nested_keys)

    return keys_list

def is_config_complete(config_file: str) -> bool:
    root_dir = Path(__file__).resolve().parent.parent

    with open(os.path.join(root_dir, 'config_templates', 'config.example.toml'), 'r') as f:
        template_config = toml.load(f)

    with open(os.path.join(root_dir, 'src', config_file), 'r') as f:
        env_config = toml.load(f)

    template_results = traverse_dict_keys(template_config)

    env_results = traverse_dict_keys(env_config)

    count = 0
    for key in template_results:
        if key not in env_results:
            count += 1
            print('Missing in config =', key)

    print('=================================')
    print('Missing config env count:', count)

    if count == 0:
        return True
    return False



    

    
