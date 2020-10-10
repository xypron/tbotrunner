from tbot.machine import connector, board, linux
import time
import tbot
from credentials import MyCredentials

class MyBoard(
    connector.ConsoleConnector,
    board.PowerControl,
    board.Board,
):
    name = "OrangePiPC"

    def poweron(self):
        self.host.exec0("relay-card", "off")
        time.sleep(3)
        self.host.exec0("sd-mux-ctrl", "-v", "0", "-td")
        self.host.exec0("relay-card", "on")

    def poweroff(self):
        self.host.exec0("relay-card", "off")

    def connect(self, mach):
        # Open the serial console
        return mach.open_channel("picocom", "-b", "115200", "/dev/serial/by-path/platform-3f980000.usb-usb-0:1.1.3:1.0-port0")

BOARD = MyBoard

class MyUBootBuilder(tbot.tc.uboot.UBootBuilder):
    name = "orangepipc"
    defconfig = "orangepi_pc_defconfig"
    toolchain = "arm"
    remote = "https://gitlab.denx.de/u-boot/u-boot.git"
    testpy_boardenv = ""

    def install(self, host, path: str):
        host.exec0("sd-mux-ctrl", "-v", "0", "-ts")
        host.exec0(f"dd", "conv=fsync,notrunc", f"if={path}/u-boot-sunxi-with-spl.bin", "of=/dev/sda", "bs=8k", "seek=1")
        pass

class MyBoardUBoot(
    board.Connector,
    board.UBootAutobootIntercept,
    board.UBootShell,
):
    prompt = "=> "
    build = MyUBootBuilder()

UBOOT = MyBoardUBoot

class MyLinux(
    board.Connector,
    board.LinuxBootLogin,
    linux.Ash,
):
    cred = MyCredentials()
    username = cred.getUsername("orangepipc")
    password = cred.getPassword("orangepipc")
    cred = None

LINUX = MyLinux
