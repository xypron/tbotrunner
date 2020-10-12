# SPDX-License-Identifier: GPL-3.0+
#
# Copyright (c) 2020  Heinrich Schuchardt <xypron.glpk@gmx.de>
# Copyright (C) 2019  Harald Seiler

import abc
import contextlib
import typing
import tbot
from tbot.machine import linux
from tbot.tc import git

H = typing.TypeVar("H", bound=linux.LinuxShell)
BH = typing.TypeVar("BH", bound=linux.Builder)

class OpenSbiBuilder(abc.ABC):
    """
    OpenSBI build process description.

    You will usually define it in your board config like this::

        class MyOpenSbiBuilder(tbot.tc.opensbi.OpenSbiBuilder):
            toolchain = "riscv64"

    To make tbot aware of this config, you need to tell it in your
    OpenSBI config::

        class MyUBootMachine(
            board.Connector,
            board.UBootShell,
        ):
            # Create a builder instance
            opensbi_build = MySbiBuilder()

    If you've done everything correctly, calling the ``opensbi_checkout``
    or ``opensbi_build`` testcases should then checkout and build OpenSBI
    for your board!

    You can also manually trigger the checkout/build of a certain
    builder using the :meth:`~tbot.tc.opensbi.UBootBuilder.checkout`
    and :meth:`~tbot.tc.opensbi.UBootBuilder.build` methods.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of this builder."""
        pass

    remote = "https://github.com/riscv/opensbi.git"
    """
    Where to fetch OpenSBI from.
    """

    revision = None
    """
    Which revision to check out.
    """

    toolchain: typing.Optional[str] = None
    """
    Name of the toolchain to be used.

    Must exist on the selected build-host.
    """

    platform: typing.Optional[str] = None
    """
    Name of the OpenSBI platform build for, e.g. "kendryte/k210"

    This value will be passed as PLATFORM parameter to the build process.
    """

    def do_build_parameters(self, bh: H) -> str[]:
        """
        Further build parameters that shall be passed.

        E.g.

        ... code-block:: Python
            [
            "FW_PAYLOAD=y",
            "FW_PAYLOAD_OFFSET=0x20000",
            "FW_PAYLOAD_PATH=../u-boot-maix/u-boot-dtb.bin"
            ]
        """
        return []

    def do_repo_path(self, bh: H) -> linux.Path[H]:
        """
        Build step that defines where the OpenSBI build-directory is.

        The default path is ``$workdir/opensbi-$name``. Overwrite this
        step to set a custom path::

            def do_repo_path(self, bh: linux.Builder) -> linux.Path:
                return bh.workdir / "projects" / "foo" / "opensbi"

        :param linux.Builder bh: Selected build-host. The returned
            path **must** be associated with this machine.
        :rtype: linux.Path
        :returns: Path to the OpenSBI build directory
        """
        return bh.workdir / f"opensbi-{self.name}"

    def do_checkout(
        self, target: linux.Path[H], clean: bool, rev: typing.Optional[str]
    ) -> git.GitRepository[H]:
        """
        Build step that defines how to checkout OpenSBI.

        Overwrite this step if you have a custom checkout procedure::

            def do_checkout(self, target: linux.Path, clean: bool) -> git.GitRepository:
                return git.GitRepository(
                    target=target,
                    url=self.remote,
                    clean=clean,
                    rev="v0.8",
                )

        :param linux.Path target:  Where to checkout OpenSBI to. This build-step
            must be able to deal with an already checked out OpenSBI source.
        :param bool clean: Whether this build-step should clean the source-dir
            (like ``git clean -fdx``).
        :param str rev: Revision to check out, or None to use the current
            revision.
        :rtype: tbot.tc.git.GitRepository
        :returns: A git repo of the checked out OpenSBI sources
        """
        return git.GitRepository(target=target, url=self.remote, clean=clean, rev=rev)

    def do_patch(self, repo: git.GitRepository[H]) -> None:
        """
        Build step to patch the checked out OpenSBI tree.

        If you need to apply patches ontop of upstream OpenSBI, you should do
        so in this step::

            def do_patch(self, repo: git.GitRepository) -> None:
                repo.am(linux.Path(repo.host, "/path/to/patches"))
        """
        pass

    def do_toolchain(self, bh: BH) -> typing.ContextManager:
        """
        Build step to enable the toolchain.

        This step should return a context-manager for a sub-shell which has
        the toolchain enabled. By default this step returns
        ``bh.enable(self.toolchain)``.
        """
        if self.toolchain is None:
            tbot.log.warning("No toolchain set, building native ...")
            return bh.subshell()
        else:
            return bh.enable(self.toolchain)

    def do_build(self, bh: BH, repo: git.GitRepository[BH]) -> None:
        """
        Build step to actually build OpenSBI.

        By default, this steps runs ``make -j $(nproc)``.
        """
        nproc = int(bh.exec0("nproc", "--all"))
        params = do_build_parameters(bh)
        bh.exec0("make", "-j", str(nproc), f"PLATFORM={self.platform}", *params)

