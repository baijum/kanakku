import os
import tomllib

def load_config(file_path: str) -> dict | None:
    """
    Reads a TOML configuration file and returns its contents as a Python dictionary.

    Args:
        file_path: The path to the TOML configuration file.

    Returns:
        A dictionary representing the configuration, or None if the library
        is missing or an error occurs during parsing.
    """

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    try:
        with open(file_path, "rb") as f:
            config_data = tomllib.load(f)
        return config_data
    except tomllib.TOMLDecodeError as e:
        print(f"Error decoding TOML file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
        return None