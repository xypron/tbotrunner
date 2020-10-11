""" Lab definition
"""
import os
import socket
import typing
import tbot
from tbot.machine import connector, linux

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
            "arm": linux.build.DistroToolchain("arm", "arm-linux-gnueabihf-"),
            "arm64": linux.build.DistroToolchain("arm64", "aarch64-linux-gnu-"),
            "riscv": linux.build.DistroToolchain("riscv", "riscv64-linux-gnu-"),
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
