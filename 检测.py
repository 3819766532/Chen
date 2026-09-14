# ============================================================
# 免责声明：本代码仅供学习交流使用，请勿用于非法用途。
# 使用本代码所产生的一切后果由使用者自行承担，
# 作者不承担任何法律责任。
# ============================================================

import subprocess
import os
import shutil
import tempfile

class GitUtils:
    def __init__(self):
        self.prev_branch = None

    def ensure_clean_worktree(self):
        proc = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError("git not available or not a repo")
        if proc.stdout.strip():
            raise RuntimeError("worktree not clean. Commit or stash changes first.")

    def create_branch(self, branch):
        self.prev_branch = self._current_branch()
        subprocess.check_call(["git", "checkout", "-b", branch])
        print(f"[git] created and switched to {branch}")

    def apply_patch(self, patch_obj, commit_msg="auto-fix"):
        patch_text = patch_obj.get("patch_text")
        if not patch_text:
            return False
        # write patch to temp file and git apply
        fd, path = tempfile.mkstemp(suffix=".patch")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(patch_text)
        try:
            subprocess.check_call(["git", "apply", path])
            subprocess.check_call(["git", "add", "-A"])
            subprocess.check_call(["git", "commit", "-m", commit_msg])
            print("[git] patch applied and committed")
            return True
        except subprocess.CalledProcessError as e:
            print("[git] apply failed:", e)
            return False
        finally:
            os.remove(path)

    def push_branch(self, branch, remote="origin"):
        subprocess.check_call(["git", "push", "-u", remote, branch])

    def checkout_previous(self):
        if self.prev_branch:
            subprocess.check_call(["git", "checkout", self.prev_branch])
            print(f"[git] checked out previous branch {self.prev_branch}")

    def _current_branch(self):
        proc = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        return proc.stdout.strip()