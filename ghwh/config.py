from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    databricks_workspace_host: str = Field(min_length=1)
    databricks_api_token: SecretStr = Field(min_length=1)
    catalog_name: str = Field(min_length=1)
    volume_path: str = Field(min_length=1)
    sql_warehouse_http_path: str = Field(min_length=1)


try:
    settings = Settings()          # module level => fails at import
except ValidationError as exc:
    names = sorted(
        ".".join(str(p) for p in e["loc"]).upper() for e in exc.errors()
    )
    raise RuntimeError(
        "ghwh.config: missing or invalid environment variables: "
        + ", ".join(names)
        + " — copy .env.example to .env and fill it in."
    ) from None    # `from None` so the original (value-bearing) error is dropped

print(Settings().dict()["databricks_api_token"].get_secret_value())
