import argparse
import logging
import json
import yaml
import os
from jsonschema import validate, ValidationError, SchemaError
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the CLI.
    """
    parser = argparse.ArgumentParser(description="Validates API request/response structures against schema definitions.")
    parser.add_argument("data_file", help="Path to the API request/response data file (JSON or YAML).")
    parser.add_argument("schema_file", help="Path to the OpenAPI or schema definition file (JSON or YAML).")
    parser.add_argument("--data_type", choices=['json', 'yaml'], help="Specify the data file type (json or yaml).  Inferred from extension if omitted.")
    parser.add_argument("--schema_type", choices=['json', 'yaml'], help="Specify the schema file type (json or yaml).  Inferred from extension if omitted.")
    parser.add_argument("--log_level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help="Set the logging level.")
    return parser

def load_data(file_path: str, file_type: Optional[str] = None) -> dict:
    """
    Loads data from a JSON or YAML file.

    Args:
        file_path (str): The path to the file.
        file_type (Optional[str]): The explicit file type. If None, infered from extension.

    Returns:
        dict: The loaded data as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file type is not supported.
        Exception: For any other loading errors.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_type is None:
        file_type = file_path.split('.')[-1].lower()

    try:
        with open(file_path, 'r') as f:
            if file_type == 'json':
                return json.load(f)
            elif file_type == 'yaml' or file_type == 'yml':
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file type: {file_type}.  Must be json or yaml/yml.")
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in {file_path}: {e}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error decoding YAML in {file_path}: {e}")
        raise
    except Exception as e:
        logging.error(f"Error loading data from {file_path}: {e}")
        raise

def validate_data(data: dict, schema: dict) -> None:
    """
    Validates the data against the schema.

    Args:
        data (dict): The data to validate.
        schema (dict): The schema to validate against.

    Raises:
        ValidationError: If the data does not conform to the schema.
        SchemaError: If the schema is invalid.
    """
    try:
        validate(instance=data, schema=schema)
        logging.info("Data validation successful.")
    except ValidationError as e:
        logging.error(f"Data validation failed: {e}")
        raise
    except SchemaError as e:
        logging.error(f"Schema validation failed: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred during validation: {e}")
        raise

def main():
    """
    Main function to parse arguments, load data and schema, and validate.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(args.log_level)

    try:
        data = load_data(args.data_file, args.data_type)
        schema = load_data(args.schema_file, args.schema_type)
        validate_data(data, schema)
        print("Validation successful!")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except ValidationError as e:
        print(f"Validation Error: {e}")
        exit(1)
    except SchemaError as e:
        print(f"Schema Error: {e}")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()

# Example usage:
# 1.  Create sample data and schema files:
#     - data.json:  {"name": "John Doe", "age": 30}
#     - schema.json: {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}, "required": ["name", "age"]}
# 2.  Run the validator:
#     python main.py data.json schema.json
#
# 3. For YAML:
#     - data.yaml: name: John Doe\nage: 30
#     - schema.yaml: type: object\nproperties:\n  name:\n    type: string\n  age:\n    type: integer\nrequired: [name, age]
#     python main.py data.yaml schema.yaml
#
# 4.  Error handling:
#     - Modify data.json to have a string for age: {"name": "John Doe", "age": "30"}
#     - Run the validator again to see the validation error.