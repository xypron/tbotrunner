from tbot.machine import connector, linux, board
import typing
import tbot
import os
import socket

class MyToolChain(linux.build.Toolchain):

    def __init__(self, arch: str, prefix: str) -> None:
        self.arch = arch
        self.prefix = prefix

    def enable(self, host) -> None:
        host.exec0("export", 'CROSS_COMPILE={}'.format(self.prefix));
        pass

class MyLabHost(
    connector.SubprocessConnector,
    linux.Bash,
    linux.Lab,
):
    name = socket.gethostname()

    @property
    def workdir(self):
        return linux.Workdir.static(self, f"/tmp/tbot-workdir")

    @property
    def toolchains(self) -> typing.Dict[str, linux.build.Toolchain]:
        tbot.log.message(tbot.log.c("Message").yellow.bold + ": MyLabHost.toolchains")
        return {
            "arm": MyToolChain("arm", "arm-linux-gnueabihf-"),
        }

    def build(self):
        tbot.log.message(tbot.log.c("Message").yellow.bold + ": MyLabHost.build")
        return self.clone()

    def enable(self, toolchain_name):
        """
        toolchain_name: str with name of toolchain
        """

        toolchain = self.toolchains[toolchain_name]

        tbot.log.message(tbot.log.c("Toolchain").yellow.bold + ': {}'.format(toolchain_name))
        toolchain.enable(self)
        return self

# Tell tbot about the class by defining a global `LAB`
LAB = MyLabHost
