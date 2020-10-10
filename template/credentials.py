# copy this file to outside of the git repository and add it to PYTHONPATH

class MyCredentials:

    def __init__(self):
        self.username = {
            "orangepipc" : "user"
            }
        self.password = {
            "orangepipc" : "password"
            }

    def get_username(self, system: str) -> str:
        return self.username[system]

    def get_password(self, system: str) -> str:
        return self.password[system]
