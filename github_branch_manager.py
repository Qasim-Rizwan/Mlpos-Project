#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import argparse
from tabulate import tabulate

# Constants for branch protection rules
DEFAULT_PROTECTION_RULES = {
    "main": {
        "required_pull_request_reviews": {
            "required_approving_review_count": 1
        },
        "required_status_checks": {
            "strict": True,
            "contexts": ["lint", "unit-tests"]
        },
        "enforce_admins": True,
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False
    },
    "test": {
        "required_pull_request_reviews": {
            "required_approving_review_count": 1
        },
        "required_status_checks": {
            "strict": True,
            "contexts": ["lint", "unit-tests"]
        },
        "enforce_admins": True,
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False
    }
}

# Environment labels for tagging
BRANCH_ENVIRONMENTS = {
    "main": "production",
    "test": "staging",
    "dev": "development"
}

# Output directory for configuration files
OUTPUT_DIR = "branch_protection_configs"


def run_git_command(command, cwd=None):
    """Run a git command and return its output."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(command)}")
        print(f"Error message: {e.stderr}")
        return None


def check_git_repo(repo_path=None):
    """Check if the current directory or specified path is a git repository."""
    return run_git_command(["git", "rev-parse", "--is-inside-work-tree"], cwd=repo_path) == "true"


def get_default_branch(repo_path=None):
    """Get the default branch of the repository."""
    # Try getting the default branch name
    try:
        default_branch = run_git_command(["git", "symbolic-ref", "--short", "HEAD"], cwd=repo_path)
        return default_branch
    except:
        # If that fails, assume it's main or check for common names
        for branch in ["main", "master"]:
            if run_git_command(["git", "rev-parse", "--verify", branch], cwd=repo_path):
                return branch
        return None


def branch_exists(branch_name, repo_path=None):
    """Check if a branch exists in the repository."""
    try:
        result = run_git_command(["git", "rev-parse", "--verify", branch_name], cwd=repo_path)
        return result is not None
    except:
        return False


def create_branch(branch_name, source_branch, repo_path=None):
    """Create a new branch from the specified source branch."""
    # First ensure we have the latest version of the source branch
    run_git_command(["git", "fetch", "origin", source_branch], cwd=repo_path)
    
    # Check if the branch already exists
    if branch_exists(branch_name, repo_path):
        print(f"Branch '{branch_name}' already exists. Skipping creation.")
        return True
    
    # Create the new branch
    result = run_git_command(
        ["git", "checkout", "-b", branch_name, f"origin/{source_branch}"], 
        cwd=repo_path
    )
    
    if result is not None:
        # Push the branch to remote
        push_result = run_git_command(
            ["git", "push", "-u", "origin", branch_name],
            cwd=repo_path
        )
        if push_result is not None:
            print(f"Successfully created and pushed branch '{branch_name}' from '{source_branch}'")
            return True
    
    print(f"Failed to create branch '{branch_name}'")
    return False


def generate_protection_config(branch_name, repo_owner, repo_name):
    """Generate branch protection configuration for GitHub API."""
    if branch_name in DEFAULT_PROTECTION_RULES:
        config = DEFAULT_PROTECTION_RULES[branch_name]
        # Add repository and branch information
        config["repository"] = f"{repo_owner}/{repo_name}"
        config["branch"] = branch_name
        config["environment"] = BRANCH_ENVIRONMENTS.get(branch_name, "unknown")
        return config
    return None


def save_protection_configs(repo_owner, repo_name, branches=["main", "test"]):
    """Save branch protection configurations to JSON files."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    saved_configs = []
    
    for branch in branches:
        config = generate_protection_config(branch, repo_owner, repo_name)
        if config:
            config_file = os.path.join(OUTPUT_DIR, f"{branch}_protection.json")
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            saved_configs.append({
                "branch": branch,
                "file": config_file,
                "environment": config.get("environment")
            })
            print(f"Saved protection config for '{branch}' to {config_file}")
    
    return saved_configs


def apply_protection_with_github_api(repo_owner, repo_name, token, branches=["main", "test"]):
    """Apply branch protection rules using GitHub API."""
    # This function is a placeholder for GitHub API implementation
    # It would require a GitHub token and the 'requests' library
    print("Warning: GitHub API integration requires a token. This functionality is not implemented.")
    print("Please use the generated JSON files as a reference to manually apply protection rules through the GitHub UI.")
    return False


def main():
    parser = argparse.ArgumentParser(description="Manage Git branches and protection rules.")
    parser.add_argument("--owner", required=True, help="Repository owner (username or organization)")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--path", default=".", help="Path to the local repository (default: current directory)")
    parser.add_argument("--token", help="GitHub token (optional, for applying protection rules)")
    
    args = parser.parse_args()
    
    # Validate repository
    if not check_git_repo(args.path):
        print(f"Error: The directory '{args.path}' is not a git repository.")
        sys.exit(1)
    
    # Get default branch
    default_branch = get_default_branch(args.path)
    if not default_branch:
        print("Error: Could not determine the default branch.")
        sys.exit(1)
    
    print(f"Repository: {args.owner}/{args.repo}")
    print(f"Default branch: {default_branch}")
    
    # Create dev and test branches
    branches_created = []
    if create_branch("dev", default_branch, args.path):
        branches_created.append(("dev", "development", "Created"))
    
    if create_branch("test", default_branch, args.path):
        branches_created.append(("test", "staging", "Created"))
    
    # Add the default branch to the list
    branches_created.append((default_branch, "production", "Exists"))
    
    # Save protection configurations
    saved_configs = save_protection_configs(args.owner, args.repo, ["main", "test"])
    
    # Attempt to apply protection rules if token is provided
    if args.token:
        os.environ["GITHUB_TOKEN"] = args.token
        apply_protection_with_github_api(args.owner, args.repo, args.token)
    
    # Print summary
    print("\n=== Branch Management Summary ===")
    headers = ["Branch", "Environment", "Status"]
    print(tabulate(branches_created, headers=headers, tablefmt="grid"))
    
    print("\n=== Protection Rules ===")
    if saved_configs:
        config_table = []
        for config in saved_configs:
            config_table.append([
                config["branch"],
                config["environment"],
                "Config saved" if os.path.exists(config["file"]) else "Failed"
            ])
        print(tabulate(config_table, headers=["Branch", "Environment", "Status"], tablefmt="grid"))
        
        print("\nBranch Protection Details:")
        for branch, details in DEFAULT_PROTECTION_RULES.items():
            print(f"\n{branch} ({BRANCH_ENVIRONMENTS.get(branch, 'unknown')}):")
            print(f"  - Required approving reviews: {details['required_pull_request_reviews']['required_approving_review_count']}")
            print(f"  - Required status checks: {', '.join(details['required_status_checks']['contexts'])}")
            print(f"  - Force pushes allowed: {details['allow_force_pushes']}")
            print(f"  - Deletions allowed: {details['allow_deletions']}")
    else:
        print("No protection configurations were generated.")
    
    print("\nNext Steps:")
    print("1. Push these branches to your remote repository:")
    print("   git push origin dev test")
    print("2. Set up branch protection rules in GitHub:")
    print("   - Go to your repository settings")
    print("   - Navigate to 'Branches' > 'Branch protection rules'")
    print("   - Add rules according to the configurations in the 'branch_protection_configs' directory")


if __name__ == "__main__":
    main() 