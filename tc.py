""" Test cases """
import contextlib
import typing
import tbot
from tbot.machine import linux

@tbot.testcase
def install():
    """ Flash the u-boot-image to the board """
    with contextlib.ExitStack() as cx:
        lab = cx.enter_context(tbot.acquire_lab())
        host = typing.cast(linux.Builder, cx.enter_context(lab.build()))
        builder = getattr(tbot.selectable.UBootMachine, "build")
        path = builder.do_repo_path(host)
        builder.install(host, path._local_str())
