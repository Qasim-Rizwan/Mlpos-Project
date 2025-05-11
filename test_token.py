#!/usr/bin/env python3
import os
import requests

def main():
    # Get token from environment variable
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        return
    
    # Set up headers for API requests
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Test repository access
    owner = "Qasim-Rizwan"
    repo = "Mlpos-Project"
    url = f"https://api.github.com/repos/{owner}/{repo}"
    
    print(f"Testing access to repository: {owner}/{repo}")
    response = requests.get(url, headers=headers)
    
    print(f"HTTP Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Successfully accessed repository")
        repo_data = response.json()
        print(f"Repository name: {repo_data.get('name')}")
        print(f"Repository ID: {repo_data.get('id')}")
        print(f"Private: {repo_data.get('private')}")
    else:
        print("❌ Failed to access repository")
        print(f"Error message: {response.text}")
    
    # Test user permissions
    user_url = "https://api.github.com/user"
    print("\nChecking user information and permissions:")
    user_response = requests.get(user_url, headers=headers)
    
    if user_response.status_code == 200:
        print("✅ Successfully authenticated with GitHub")
        user_data = user_response.json()
        print(f"Username: {user_data.get('login')}")
    else:
        print("❌ Failed to authenticate with GitHub")
        print(f"Error message: {user_response.text}")
    
    # Test permissions for creating issues
    print("\nChecking permissions for repository operations:")
    permissions_url = f"https://api.github.com/repos/{owner}/{repo}/collaborators/{user_data.get('login')}/permission"
    permissions_response = requests.get(permissions_url, headers=headers)
    
    if permissions_response.status_code == 200:
        print("✅ Successfully retrieved permissions")
        perm_data = permissions_response.json()
        print(f"Permission level: {perm_data.get('permission')}")
    else:
        print("❌ Failed to retrieve permissions")
        print(f"Error message: {permissions_response.text}")

if __name__ == "__main__":
    main() 