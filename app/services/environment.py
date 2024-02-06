import os

from dotenv import dotenv_values

from app.services.exceptions import EnvironmentVarNotExists

ENVIRONMENT = dotenv_values(".env")


def get_env(env_name: str, prefer_local=True) -> str:
    """
    Get an environment variable from the .env file or from the operating system.
    :param env_name: Variable name to retrieve.
    :param prefer_local: Sets which value will be returned if the variable exists in both the .env and the OS.
    :return: Value of the environment variable.
    :raises EnvironmentVarNotExists: If the environment variable does not exist in the .env or the OS.
    """
    # Load local and global variables with name env_name.
    global_env = os.environ.get(env_name)
    local_env = ENVIRONMENT.get(env_name)

    # Check that env_name exists in .env or in OS.
    if not global_env and not local_env:
        raise EnvironmentVarNotExists(env_name)

    # Return local or global variable, whichever is valid, using the preference set by prefer_local.
    if prefer_local:
        return local_env or global_env
    else:
        return global_env or local_env


CMS_IP = get_env("CMS_IP")
CMS_USERNAME = get_env("CMS_USERNAME")
CMS_PASSWORD = get_env("CMS_PASSWORD")
CMS_NODES = get_env("CMS_NODES")

API_URL = get_env("API_URL")
