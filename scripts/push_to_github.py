#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_PATTERNS = [
    r"(^|/)\.env$",
    r"(^|/)venv/",
    r"(^|/)\.venv/",
    r"\.db$",
    r"__pycache__",
    r"\.pyc$",
    r"(^|/)\.DS_Store$",
    r"(^|/)instance/",
    r"\.pem$",
    r"credentials\.json$",
]

def run(cmd, cwd=ROOT, check=True, capture=False):
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        capture_output=capture,
        text=True,
    )


def have_cmd(name):
    try:
        run([name, "--version"], capture=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_blocked(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(re.search(pat, p) for pat in BLOCKED_PATTERNS)


def staged_files():
    r = run(["git", "diff", "--cached", "--name-only"], capture=True)
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def check_staged_safe():
    bad = [f for f in staged_files() if is_blocked(f)]
    if bad:
        print("\nBlocked files staged (will not commit):")
        for f in bad:
            print(f"  - {f}")
        run(["git", "reset", "HEAD", "--", *bad], check=False)
        print("Unstaged blocked paths.")
    return not bad


def git_init_if_needed():
    if (ROOT / ".git").exists():
        return
    print("Initializing git repository...")
    r = run(["git", "init", "-b", "main"], check=False)
    if r.returncode != 0:
        run(["git", "init"], check=False)
        run(["git", "checkout", "-B", "main"], check=False)


def ensure_gitignore():
    gi = ROOT / ".gitignore"
    if not gi.exists():
        print("Warning: .gitignore missing at repo root.")


def add_files():
    run(["git", "add", "-A"])
    check_staged_safe()
    r = run(["git", "diff", "--cached", "--name-only"], capture=True)
    files = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if not files:
        print("Nothing to commit.")
        return False
    print("\nFiles to commit:")
    for f in files[:60]:
        print(f"  + {f}")
    if len(files) > 60:
        print(f"  ... and {len(files) - 60} more")
    return True


def commit(message):
    run(["git", "commit", "-m", message])


def ensure_remote(repo_name, visibility):
    r = run(["git", "remote"], capture=True, check=False)
    if "origin" in r.stdout.split():
        return
    user_r = run(["gh", "api", "user", "-q", ".login"], capture=True)
    login = user_r.stdout.strip()
    if not login:
        raise SystemExit("Could not read GitHub username from gh.")
    url = f"https://github.com/{login}/{repo_name}.git"
    run(["git", "remote", "add", "origin", url])


def create_repo_if_needed(repo_name, visibility, description):
    r = run(
        ["gh", "repo", "view", repo_name, "--json", "name"],
        capture=True,
        check=False,
    )
    if r.returncode == 0:
        print(f"Repository '{repo_name}' already exists on GitHub.")
        return
    vis_flag = "--public" if visibility == "public" else "--private"
    run(
        [
            "gh",
            "repo",
            "create",
            repo_name,
            vis_flag,
            "--source=.",
            "--remote=origin",
            "--description",
            description,
        ],
        cwd=ROOT,
    )


def push(branch, set_upstream):
    cmd = ["git", "push"]
    if set_upstream:
        cmd += ["-u", "origin", branch]
    else:
        cmd += ["origin", branch]
    run(cmd)


def main():
    parser = argparse.ArgumentParser(
        description="Stage safe files, commit, and push to GitHub using git + gh."
    )
    parser.add_argument(
        "-m",
        "--message",
        default="Update GoalVault",
        help="Commit message",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Branch to push (default: main)",
    )
    parser.add_argument(
        "--repo",
        default="goalvault",
        help="GitHub repo name when creating with gh",
    )
    parser.add_argument(
        "--visibility",
        choices=["public", "private"],
        default="public",
    )
    parser.add_argument(
        "--description",
        default="GoalVault — AtomQuest Hackathon goal setting & tracking portal",
    )
    parser.add_argument(
        "--create-repo",
        action="store_true",
        help="Create GitHub repo with gh if it does not exist",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Commit only, do not push",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be staged, no commit/push",
    )
    args = parser.parse_args()

    os.chdir(ROOT)
    print(f"Repository root: {ROOT}\n")

    if not have_cmd("git"):
        sys.exit("git is not installed.")
    if not args.no_push and not have_cmd("gh"):
        print("Warning: gh CLI not found. Install from https://cli.github.com/")
        print("You can still commit locally with --no-push.")

    ensure_gitignore()
    git_init_if_needed()

    if args.dry_run:
        run(["git", "add", "--dry-run", "-A"])
        return

    if not add_files():
        return

    commit(args.message)

    if args.no_push:
        print("\nCommitted locally. Run without --no-push to upload.")
        return

    if args.create_repo:
        if not have_cmd("gh"):
            sys.exit("gh is required for --create-repo")
        create_repo_if_needed(args.repo, args.visibility, args.description)
    else:
        ensure_remote(args.repo, args.visibility)

    push(args.branch, set_upstream=True)
    print("\nDone. View on GitHub: gh repo view --web")


if __name__ == "__main__":
    main()
