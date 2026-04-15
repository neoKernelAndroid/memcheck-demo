import subprocess
import sys
from pathlib import Path

CPP_EXTS = {".c", ".cc", ".cpp", ".h", ".hpp"}


def run(cmd):
    return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="ignore").strip()


def get_staged_files():
    out = run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    files = [x.strip() for x in out.splitlines() if x.strip()]
    return [f for f in files if Path(f).suffix in CPP_EXTS]


def get_staged_content(file_path):
    try:
        return run(["git", "show", f":{file_path}"])
    except subprocess.CalledProcessError:
        return ""


def check_malloc_without_free(file_path, content):
    issues = []
    has_alloc = any(x in content for x in ["malloc(", "calloc(", "realloc(", "strdup("])
    has_free = "free(" in content

    if has_alloc and not has_free:
        issues.append({
            "rule_id": "NMLEAK001",
            "severity": "CRITICAL",
            "file": file_path,
            "message": "Possible malloc/calloc/realloc/strdup without free in staged file",
            "suggestion": "Add free(...) on all exit paths, or move ownership to managed object."
        })
    return issues


def main():
    files = get_staged_files()
    all_issues = []

    for f in files:
        content = get_staged_content(f)
        if not content:
            continue
        all_issues.extend(check_malloc_without_free(f, content))

    if all_issues:
        print("[memcheck] blocking issues found:\n")
        for issue in all_issues:
            print(f"[{issue['rule_id']}] {issue['severity']}")
            print(f"File: {issue['file']}")
            print(f"Problem: {issue['message']}")
            print(f"Fix: {issue['suggestion']}")
            print()
        sys.exit(1)

    print("[memcheck] passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
