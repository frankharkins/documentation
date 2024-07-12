#!/usr/bin/env python3

# This code is a Qiskit project.
#
# (C) Copyright IBM 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import logging
import shutil
from argparse import ArgumentParser
from pathlib import Path

logger = logging.getLogger(__name__)

from utils import configure_logging, run_subprocess, setup_git_account, switch_branch


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "folder", help="the folder to deploy to GitHub Pages", type=Path
    )
    return parser


def main() -> None:
    folder: Path = create_parser().parse_args().folder
    if not folder.exists():
        raise AssertionError(
            f"Expected {folder} to have been created with the new content"
        )
    setup_git_account()

    # Handle if the content folder already exists on gh-pages branch.
    run_subprocess(["git", "stash", "--include-untracked"])
    with switch_branch("gh-pages"):
        if folder.exists():
            shutil.rmtree(folder)
        run_subprocess(["git", "stash", "pop"])

        changed_files = run_subprocess(["git", "status", "--porcelain"]).stdout.strip()
        if not changed_files:
            logger.info("No changed files detected, so no push made to gh-pages")
            return

        run_subprocess(["git", "add", "."])
        run_subprocess(["git", "commit", "-m", f"Deploy PR preview for {folder}"])
        run_subprocess(["git", "push"])
        logger.info("Pushed updates to gh-pages branch")


if __name__ == "__main__":
    configure_logging()
    main()
