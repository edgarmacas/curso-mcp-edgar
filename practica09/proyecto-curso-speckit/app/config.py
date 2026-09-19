from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = "clave_secreta_por_defecto_para_desarrollo_insegura"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./gastos.db"
    DEMO_USER_EMAIL: str = "demo@gastos.local"
    LOG_LEVEL: str = "INFO"
    MCP_DEMO_EMAIL: str = "demo@curso.com"
    MCP_DEMO_PASSWORD: str = "demo1234"
    MCP_ISSUER_URL: str = "http://127.0.0.1:8000"
    MCP_RESOURCE_URL: str = "http://127.0.0.1:8000/mcp"

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY

    @property
    def access_token_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def log_level(self) -> str:
        return self.LOG_LEVEL

    @property
    def mcp_demo_email(self) -> str:
        return self.MCP_DEMO_EMAIL

    @property
    def mcp_demo_password(self) -> str:
        return self.MCP_DEMO_PASSWORD

    @property
    def mcp_issuer_url(self) -> str:
        return self.MCP_ISSUER_URL

    @property
    def mcp_resource_url(self) -> str:
        return self.MCP_RESOURCE_URL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
