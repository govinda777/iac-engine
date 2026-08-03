#!/usr/bin/env python3
import os
import re
import sys

# Color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_error(msg):
    print(f"{RED}ERROR: {msg}{RESET}", file=sys.stderr)

def print_warning(msg):
    print(f"{YELLOW}WARNING: {msg}{RESET}")

def print_success(msg):
    print(f"{GREEN}SUCCESS: {msg}{RESET}")

# 1. Regex to check for hardcoded AWS credentials
# We look for common patterns representing static AWS Access Keys or Secret Keys
AWS_ACCESS_KEY_RE = re.compile(r'(?i)aws_access_key_id\s*=\s*["\'](AKIA[A-Z0-9]{16})["\']')
AWS_SECRET_KEY_RE = re.compile(r'(?i)aws_secret_access_key\s*=\s*["\'][A-Za-z0-9/+=]{40}["\']')
GENERIC_AWS_KEY_RE = re.compile(r'(?i)(AKIA[0-9A-Z]{16})')

def check_file_for_credentials(filepath):
    """
    Checks a single file for hardcoded AWS access keys or secret keys.
    Returns True if no issues found, False otherwise.
    """
    has_issues = False
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_no, line in enumerate(f, 1):
                # Ignore comments
                clean_line = line.strip()
                if clean_line.startswith("#") or clean_line.startswith("//") or clean_line.startswith("/*"):
                    continue

                if AWS_ACCESS_KEY_RE.search(line) or AWS_SECRET_KEY_RE.search(line) or (GENERIC_AWS_KEY_RE.search(line) and "AKIA" in line):
                    print_error(f"Possible hardcoded AWS Credentials found in {filepath}:{line_no} -> {clean_line}")
                    has_issues = True
    except Exception as e:
        print_warning(f"Could not read {filepath}: {e}")
    return not has_issues

# 2. Check that the backend "s3" configuration is properly decentralized
# It must contain use_lockfile = true to use S3 Native Locking.
BACKEND_BLOCK_RE = re.compile(r'backend\s+"s3"\s*\{([^}]*)\}')

def check_decentralized_backend(filepath):
    """
    Ensures that any backend "s3" declaration in a .tf file contains use_lockfile = true.
    Returns True if valid (either no S3 backend or valid S3 backend), False if invalid.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        matches = BACKEND_BLOCK_RE.findall(content)
        for match in matches:
            # Strip comments and whitespaces to check for use_lockfile
            clean_block = re.sub(r'#.*|//.*|/\*.*?\*/', '', match, flags=re.DOTALL)

            # Simple check for use_lockfile = true
            if not re.search(r'use_lockfile\s*=\s*true', clean_block, re.IGNORECASE):
                print_error(f"Invalid S3 backend block found in {filepath}:")
                print_error(f"Found content: {match.strip()}")
                print_error("Under the decentralized engine paradigm, Spokes must declare their own S3 backend and include 'use_lockfile = true'.")
                return False
    except Exception as e:
        print_warning(f"Could not check decentralized backend status for {filepath}: {e}")
    return True

def run_lint_security(directory="."):
    """
    Scans the directory for .tf and .tfvars files and applies security linting.
    """
    print("=========================================")
    print("🚀 iac-engine: Starting Security Lint Validation")
    print("=========================================")

    tf_files = []
    for root, _, files in os.walk(directory):
        # Ignore git directories
        if ".git" in root or ".terraform" in root:
            continue
        for file in files:
            if file.endswith(".tf") or file.endswith(".tfvars") or file.endswith(".tfvars.json"):
                tf_files.append(os.path.join(root, file))

    if not tf_files:
        print("No Terraform files (.tf, .tfvars) found to lint.")
        return True

    success = True
    for filepath in tf_files:
        # Check for static credentials
        if not check_file_for_credentials(filepath):
            success = False

        # Check decentralized backend configuration for .tf files
        if filepath.endswith(".tf"):
            if not check_decentralized_backend(filepath):
                success = False

    if success:
        print_success("All files passed the security lint validation! No hardcoded keys found and S3 backends are properly decentralized (with use_lockfile=true).")
    else:
        print_error("Security lint validation failed! Please fix the errors listed above before committing.")

    print("=========================================")
    return success

if __name__ == "__main__":
    # If a specific directory is passed as an argument, use it; otherwise, use current directory.
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if not run_lint_security(target_dir):
        sys.exit(1)
    sys.exit(0)
