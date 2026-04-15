import json
import subprocess
import sys
from pathlib import Path

BUILD_DIR = Path("build")
COMPILE_DB = BUILD_DIR / "compile_commands.json"


def run_cmd(cmd, allow_fail=False):
    print("[run]", " ".join(cmd))
    result = subprocess.run(cmd, text=True, encoding="utf-8", errors="ignore")
    if result.returncode != 0 and not allow_fail:
        sys.exit(result.returncode)
    return result.returncode


def load_compile_db():
    if not COMPILE_DB.exists():
        print(f"[memcheck] compile_commands.json not found: {COMPILE_DB}")
        sys.exit(1)
    return json.loads(COMPILE_DB.read_text(encoding="utf-8"))


def get_changed_cpp_files():
    cmd = ["git", "diff", "--name-only", "origin/main...HEAD"]
    out = subprocess.check_output(cmd, text=True, encoding="utf-8", errors="ignore")
    files = [x.strip() for x in out.splitlines() if x.strip()]
    exts = {".c", ".cc", ".cpp", ".h", ".hpp"}
    return [f for f in files if Path(f).suffix in exts]


def run_clang_tidy(files):
    if not files:
        return
    for f in files:
        run_cmd(["clang-tidy", f, f"-p={BUILD_DIR}"], allow_fail=True)


def run_clang_static_analyzer(files):
    if not files:
        return
    for f in files:
        run_cmd(["clang", "--analyze", f], allow_fail=True)


def simple_cross_file_hint(files):
    keywords = ["alloc", "create", "make", "getBuffer"]
    release_keywords = ["free(", "delete ", "destroy", "release("]
    issues = []
    for f in files:
        p = Path(f)
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8", errors="ignore")
        if any(k in content for k in keywords) and not any(r in content for r in release_keywords):
            issues.append({
                "rule_id": "NMLEAK201",
                "severity": "CRITICAL",
                "file": f,
                "message": "Possible cross-file ownership leak: creator-like call without visible release",
                "suggestion": "Check whether returned pointer/resource must be freed, deleted, or released."
            })
    return issues


def main():
    load_compile_db()
    files = get_changed_cpp_files()
    print(f"[memcheck] changed cpp files: {len(files)}")
    for f in files:
        print(" -", f)
    run_clang_tidy(files)
    run_clang_static_analyzer(files)
    issues = simple_cross_file_hint(files)
    if issues:
        print("\n[memcheck] custom issues found:\n")
        for issue in issues:
            print(f"[{issue['rule_id']}] {issue['severity']}")
            print(f"File: {issue['file']}")
            print(f"Problem: {issue['message']}")
            print(f"Fix: {issue['suggestion']}")
            print()
    print("[memcheck] CI scan finished")


if __name__ == "__main__":
    main()
