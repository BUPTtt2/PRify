from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str = ""
    deepseek_api_key: str = ""
    deepseek_api_url: str = "https://api.deepseek.com/v1/chat/completions"
    github_timeout: int = 30
    llm_timeout: int = 60
    max_files: int = 20
    max_diff_lines: int = 1000
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
