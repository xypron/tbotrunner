""" Lab definition
"""
import os
import socket
import typing
import tbot
from tbot.machine import connector, linux

class MyToolChain(linux.build.Toolchain):
    """ Generic Toolchain for cross compilation
    """

    def __init__(self, arch: str, prefix: str) -> None:
        self.arch = arch
        self.prefix = prefix

    def enable(self, host) -> None:
        """ Enable selected Toolchain
        """
        host.exec0("export", 'CROSS_COMPILE={}'.format(self.prefix))

class MyLabHost(
        connector.SubprocessConnector,
        linux.Bash,
        linux.Lab,
    ):
    """ Generic Lab definition
    """
    name = socket.gethostname()

    @property
    def workdir(self):
        mypath = os.path.dirname(os.path.realpath(__file__)) + '/tbot-workdir'
        return linux.Workdir.static(self, mypath)

    @property
    def toolchains(self) -> typing.Dict[str, linux.build.Toolchain]:
        """ Define Toolchains
        """
        return {
            "arm": MyToolChain("arm", "arm-linux-gnueabihf-"),
            "arm64": MyToolChain("arm64", "aarch64-linux-gnu-"),
            "riscv": MyToolChain("riscv", "riscv64-linux-gnu-"),
        }

    def build(self):
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
