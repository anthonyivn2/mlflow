from dataclasses import dataclass
from typing import Any


def _normalize_schema(schema: Any) -> dict[str, Any] | None:
    if schema is None:
        return None
    if isinstance(schema, dict):
        return schema
    if hasattr(schema, "model_json_schema"):
        return schema.model_json_schema()
    raise TypeError(
        f"Schema must be a dict (JSON Schema) or a Pydantic BaseModel class, got {type(schema)}"
    )


@dataclass
class AgentInfo:
    """Metadata describing an agent server and a ResponsesAgent's identity/interface.

    Args:
        name: Server or app name for `/agent/info`. Defaults to the app name when omitted.
        use_case: Declared agent use case. Defaults to `agent` for `/agent/info`.
        mlflow_version: MLflow version served by the endpoint.
        agent_api: Agent API served by the endpoint, for example `responses`.
        description: Human-readable description of what the agent does.
        version: Version string for the agent.
        metadata: Arbitrary metadata for extensibility. Reserved keys may include
            `custom_inputs_schema` and `custom_outputs_schema`, each as a JSON Schema
            dict or Pydantic BaseModel class.
        tags: Arbitrary key-value metadata for extensibility.
    """

    name: str | None = None
    use_case: str | None = None
    mlflow_version: str | None = None
    agent_api: str | None = None
    description: str | None = None
    version: str | None = None
    metadata: dict[str, Any] | None = None
    tags: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.name is not None:
            result["name"] = self.name
        if self.use_case is not None:
            result["use_case"] = self.use_case
        if self.mlflow_version is not None:
            result["mlflow_version"] = self.mlflow_version
        if self.agent_api is not None:
            result["agent_api"] = self.agent_api
        if self.description is not None:
            result["description"] = self.description
        if self.version is not None:
            result["version"] = self.version

        if self.metadata is not None:
            metadata = dict(self.metadata)
            if "custom_inputs_schema" in metadata:
                metadata["custom_inputs_schema"] = _normalize_schema(metadata["custom_inputs_schema"])
            if "custom_outputs_schema" in metadata:
                metadata["custom_outputs_schema"] = _normalize_schema(
                    metadata["custom_outputs_schema"]
                )
            result["metadata"] = metadata

        if self.tags is not None:
            result["tags"] = self.tags
        return result

