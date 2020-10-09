import contextlib
import tbot

@tbot.testcase
def install():
    """ Flash the u-boot-image to the board """
    with contextlib.ExitStack() as cx:
        lab = cx.enter_context(tbot.acquire_lab())
        host = typing.cast(BH, cx.enter_context(lab.build()))
        builder = getattr(tbot.selectable.UBootMachine, "build")
        path = builder.do_repo_path(host)
        builder.install(host, path._local_str())
