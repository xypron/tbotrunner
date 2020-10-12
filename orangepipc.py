""" Board configuration module for the OrangePi PC.
"""
import time
import tbot
from tbot.machine import connector, board, linux
from tbot.tc import git, kconfig
from credentials import MyCredentials

class MyBoard(
        connector.ConsoleConnector,
        board.PowerControl,
        board.Board,
    ):
    """ Board definition for the OrangePi PC.
    """

    name = "OrangePiPC"

    def poweron(self):
        self.host.exec0("relay-card", "off")
        self.host.exec0("sd-mux-ctrl", "-v", "0", "-td")
        time.sleep(3)
        self.host.exec0("relay-card", "on")

    def poweroff(self):
        self.host.exec0("relay-card", "off")

    def connect(self, mach):
        # Open the serial console
        return mach.open_channel(
            "picocom", "-b", "115200",
            "/dev/serial/by-path/platform-3f980000.usb-usb-0:1.1.3:1.0-port0")

    def clone(self):
        raise NotImplementedError("Cannot clone serial connection")

BOARD = MyBoard

class MyUBootBuilder(tbot.tc.uboot.UBootBuilder):
    """ Builder for the OrangePi PC.
    """
    name = "orangepipc"
    defconfig = "orangepi_pc_defconfig"
    toolchain = "arm"
    remote = "https://gitlab.denx.de/u-boot/u-boot.git"
    testpy_boardenv = ""


    # def do_configure(self, bh: linux.Builder,
    def do_configure(self, bh, repo) -> None:
        super().do_configure(bh, repo)

        tbot.log.message(tbot.log.c("Toolchain").yellow.bold +
                         ': Patching configuration')
        kconfig.enable(repo / ".config", "CONFIG_CMD_BOOTEFI_SELFTEST")
        kconfig.enable(repo / ".config", "CONFIG_CMD_BOOTEFI_HELLO")
        kconfig.enable(repo / ".config", "CONFIG_CMD_NVEDIT_EFI")
        kconfig.enable(repo / ".config", "CONFIG_CMD_EFIDEBUG")
        kconfig.enable(repo / ".config", "CONFIG_UNIT_TEST")
        bh.exec0("make", "olddefconfig")

    def do_checkout(self, target, clean, rev) -> git.GitRepository:
        branch = "master"
        return git.GitRepository(
            target=target, url=self.remote, clean=clean, rev=branch
        )

    def install(self, host, path: str):
        """ Copy image to SD card.
        """
        host.exec0("sd-mux-ctrl", "-v", "0", "-ts")
        time.sleep(3)
        host.exec0(
            f"dd", "conv=fsync,notrunc",
            f"if={path}/u-boot-sunxi-with-spl.bin", "of=/dev/sda",
            "bs=8k", "seek=1")

class MyBoardUBoot(
        board.Connector,
        board.UBootAutobootIntercept,
        board.UBootShell,
    ):
    """ U-Boot testing for the OrangePi PC.
    """
    prompt = "=> "
    build = MyUBootBuilder()

UBOOT = MyBoardUBoot

class MyLinux(
        board.Connector,
        board.LinuxBootLogin,
        linux.Ash,
    ):
    """ Linux testing for the OrangePi PC.
    """
    cred = MyCredentials()
    username = cred.get_username("orangepipc")
    password = cred.get_password("orangepipc")
    cred = None

LINUX = MyLinux
