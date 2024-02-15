class EnvironmentVarNotExists(Exception):
    """
    Raised when an environment variable is not defined in the .env file or the operating system.
    """

    def __init__(self, env_var: str):
        self.env_var = env_var

    def __str__(self):
        return f"Environment variable '{self.env_var}' does not exist."


class CmsAuthenticationFailure(Exception):
    """
    Exception raised when login to cms fails.
    """

    def __init__(self, username, ip):
        self.username = username
        self.ip = ip

    def __str__(self):
        return f"AUTHENTICATION FAILED FOR USER={self.username} @ IP={self.ip}"


class CmsDeauthenticationFailure(Exception):
    """
    Exception raised when logout to cms fails.
    """

    def __init__(self, username, ip):
        self.username = username
        self.ip = ip

    def __str__(self):
        return f"DEAUTHENTICATION FAILED FOR USER={self.username} @ IP={self.ip}"


class CmsCommunicationFailure(Exception):
    """
    Exception raised when a cms request fails because of an invalid request or no connection.
    """

    def __init__(self, url):
        self.url = url

    def __str__(self):
        return f"REQUEST FOR CMS SERVER {self.url} FAILED"
