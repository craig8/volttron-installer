from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load dev environment variables if dev.env exists otherwise
# load production .env file
if Path("dev.env").exists():
    load_dotenv("dev.env")
elif Path(".env").exists():
    load_dotenv()
else:
    raise FileNotFoundError("No .env nore dev.env file found")


class _InstallerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VI_")

    log_level: str = Field(default="DEBUG")
    secret_key: str = Field()
    app_name: str = Field()
    upload_dir: str = Field()


__settings__ = _InstallerSettings()
def get_settings() -> _InstallerSettings:
    return __settings__

