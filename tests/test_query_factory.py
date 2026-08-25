import pytest

from envel.exceptions import errors
from envel.factories.query import load_search_query

VALID_YAML = """
queries:
  - name: "upwork-python-backend"
    sender:
      - "team@upwork.com"
    subject_contains:
      - "new job"
  - name: "upwork-fastapi-parsing"
    sender:
      - "team@upwork.com"
"""

MALFORMED_YAML = """
queries:
  - name: "broken
    sender: [unclosed
"""

MISSING_QUERIES_KEY_YAML = """
searches:
  - name: "wrong-key"
"""

INVALID_FIELD_TYPE_YAML = """
queries:
  - name: "bad-sender-type"
    sender: "not-a-list"
"""


def _write(tmp_path, content: str) -> str:
    config_path = tmp_path / "query_config.yaml"
    config_path.write_text(content, encoding="utf-8")
    return str(config_path)


def test_missing_file_raises_query_config_file_error(tmp_path):
    missing_path = str(tmp_path / "does_not_exist.yaml")
    with pytest.raises(errors.QueryConfigFileError):
        load_search_query(config_file=missing_path)


def test_malformed_yaml_raises_query_config_file_error(tmp_path):
    config_file = _write(tmp_path, MALFORMED_YAML)
    with pytest.raises(errors.QueryConfigFileError):
        load_search_query(config_file=config_file)


def test_missing_queries_key_raises_query_config_file_error(tmp_path):
    config_file = _write(tmp_path, MISSING_QUERIES_KEY_YAML)
    with pytest.raises(errors.QueryConfigFileError):
        load_search_query(config_file=config_file)


def test_index_out_of_range_raises_query_config_file_error(tmp_path):
    config_file = _write(tmp_path, VALID_YAML)
    with pytest.raises(errors.QueryConfigFileError):
        load_search_query(config_file=config_file, index=5)


def test_invalid_field_type_raises_query_config_file_error(tmp_path):
    config_file = _write(tmp_path, INVALID_FIELD_TYPE_YAML)
    with pytest.raises(errors.QueryConfigFileError):
        load_search_query(config_file=config_file)


def test_valid_yaml_returns_search_query_at_default_index(tmp_path):
    config_file = _write(tmp_path, VALID_YAML)
    result = load_search_query(config_file=config_file)
    assert result.name == "upwork-python-backend"
    assert result.sender == ["team@upwork.com"]


def test_valid_yaml_returns_search_query_at_given_index(tmp_path):
    config_file = _write(tmp_path, VALID_YAML)
    result = load_search_query(config_file=config_file, index=1)
    assert result.name == "upwork-fastapi-parsing"
