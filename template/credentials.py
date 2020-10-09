# copy this file to outside of the git repository and add it to PYTHONPATH

class MyCredentials:

    def __init__(self):
        self.username = {
            "orangepipc" : "user"
            }
        self.password = {
            "orangepipc" : "password"
            }

    def getUsername(self, system :str) -> str:
        return self.username[system]

    def getPassword(self, system: str) -> str:
        return self.password[system]
