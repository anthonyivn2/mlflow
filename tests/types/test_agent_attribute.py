import pytest
from pydantic import BaseModel

from mlflow.types.agent_attribute import AgentInfo, _normalize_schema


class SampleInputs(BaseModel):
    strategy: str
    max_depth: int = 5


class SampleOutputs(BaseModel):
    result: str
    confidence: float


def test_default_fields_are_none():
    attr = AgentInfo()
    assert attr.name is None
    assert attr.description is None
    assert attr.version is None
    assert attr.metadata is None
    assert attr.tags is None


def test_to_dict_with_all_fields():
    attr = AgentInfo(
        name="planner",
        description="Plans multi-step tasks",
        version="1.0",
        metadata={
            "custom_inputs_schema": {"type": "object", "properties": {"x": {"type": "string"}}},
            "custom_outputs_schema": {
                "type": "object",
                "properties": {"y": {"type": "number"}},
            },
            "team_config": {"routing": "planner"},
        },
        tags={"team": "ml", "env": "prod"},
    )
    result = attr.to_dict()
    assert result["name"] == "planner"
    assert result["description"] == "Plans multi-step tasks"
    assert result["version"] == "1.0"
    assert result["metadata"]["custom_inputs_schema"] == {
        "type": "object",
        "properties": {"x": {"type": "string"}},
    }
    assert result["metadata"]["custom_outputs_schema"] == {
        "type": "object",
        "properties": {"y": {"type": "number"}},
    }
    assert result["metadata"]["team_config"] == {"routing": "planner"}
    assert result["tags"] == {"team": "ml", "env": "prod"}


def test_to_dict_omits_none():
    attr = AgentInfo(name="planner")
    result = attr.to_dict()
    assert result == {"name": "planner"}
    assert "description" not in result
    assert "version" not in result
    assert "metadata" not in result
    assert "tags" not in result


@pytest.mark.parametrize(
    ("schema", "expected_type"),
    [
        (None, type(None)),
        ({"type": "object"}, dict),
        (SampleInputs, dict),
    ],
)
def test_normalize_schema(schema, expected_type):
    result = _normalize_schema(schema)
    if schema is None:
        assert result is None
    else:
        assert isinstance(result, expected_type)


def test_normalize_schema_dict_passthrough():
    raw = {"type": "object", "properties": {"x": {"type": "string"}}}
    assert _normalize_schema(raw) is raw


def test_normalize_schema_pydantic():
    result = _normalize_schema(SampleInputs)
    assert result == SampleInputs.model_json_schema()
    assert "properties" in result
    assert "strategy" in result["properties"]
    assert "max_depth" in result["properties"]


def test_normalize_schema_invalid_type():
    with pytest.raises(TypeError, match="Schema must be a dict"):
        _normalize_schema("not a schema")


def test_to_dict_with_pydantic_schemas():
    attr = AgentInfo(
        name="planner",
        metadata={
            "custom_inputs_schema": SampleInputs,
            "custom_outputs_schema": SampleOutputs,
        },
    )
    result = attr.to_dict()
    assert result["metadata"]["custom_inputs_schema"] == SampleInputs.model_json_schema()
    assert result["metadata"]["custom_outputs_schema"] == SampleOutputs.model_json_schema()
