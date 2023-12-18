import pathlib

try:
    import tomllib
except Exception:
    import toml as tomllib

from pydantic_settings import BaseSettings, SettingsConfigDict

path = pathlib.Path(__file__).parent.absolute()
with open(f"{path}/../pyproject.toml", mode="rb") as f:
    try:
        project_data = tomllib.load(f)
    except Exception:
        project_data = tomllib.load("".join(f.readlines()))

app_version = project_data["tool"]["poetry"]["version"]
app_name = project_data["tool"]["poetry"]["name"]
app_title = project_data["tool"]["metadata"]["title"]
app_description = project_data["tool"]["metadata"]["full_description"]


class Settings(BaseSettings):
    environment: str = "production"
    logging_level: str = "INFO"
    root_path: str = ""
    palm_key: str
    palm_model: str = "models/text-bison-001"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
