import yaml

def read_config(file_path, config):
    print(f"Reading configuration from: {file_path}")
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data[config]
    except FileNotFoundError:
        print(f"Error: File not found -> {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None