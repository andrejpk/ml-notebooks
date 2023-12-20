
import os


def get_env_var(var_name:str) -> str:
	value = os.getenv(var_name)
	if value is None:
		raise ValueError(f"{var_name} environment variable is not set; set in .env or in env var")
	return value
