from pathlib import Path

import yaml
from pydantic import ValidationError

from envel.exceptions import errors
from envel.schemas.query import SearchQuery


def load_search_query(config_file: str, index: int = 0) -> SearchQuery:
    config_path = Path(config_file)
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise errors.QueryConfigFileError(
            "'query_config.yaml' file could not be found."
        ) from e
    except yaml.YAMLError as e:
        raise errors.QueryConfigFileError(
            "Invalid YAML file content. HINT: Ensure the indentations and other YAML format requirements."
        ) from e

    try:
        query_list = data["queries"]
    except KeyError as e:
        raise errors.QueryConfigFileError(
            "Invalid YAML file content. HINT: Ensure the file begins with the title 'queries'."
        ) from e


    try:
        entry = query_list[index]
        return SearchQuery(**entry)
    except IndexError as e:
        raise errors.QueryConfigFileError(
            f"Request out of Query Config list index, Query Config has only {len(query_list)} entries."
        ) from e
    except ValidationError as e:
        raise errors.QueryConfigFileError(
            "Invalid YAML file content. HINT: Ensure the field names match with the example."
        ) from e