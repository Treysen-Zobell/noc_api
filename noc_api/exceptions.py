
class EnvironmentVarNotExists(Exception):
    """
    Raised when an environment variable is not defined in the .env file or the operating system.
    """
    def __init__(self, env_var: str):
        self.env_var = env_var

    def __str__(self):
        return f"Environment variable '{self.env_var}' does not exist."
