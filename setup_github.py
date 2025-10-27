#!/usr/bin/env python3
"""
GitHub Setup Script
Initializes git repository and pushes to GitHub
"""

import os
import subprocess
import sys
from pathlib import Path


class GitHubSetup:
    """Handle GitHub repository setup and deployment"""
    
    def __init__(self, repo_name="rag-latex-generator"):
        self.repo_name = repo_name
        self.repo_dir = Path.cwd()
        
    def check_git_installed(self):
        """Check if git is installed"""
        try:
            subprocess.run(["git", "--version"], 
                         capture_output=True, check=True)
            print("✓ Git is installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ Git is not installed. Please install git first.")
            return False
    
    def init_repository(self):
        """Initialize git repository"""
        if (self.repo_dir / ".git").exists():
            print("✓ Git repository already initialized")
            return True
        
        try:
            subprocess.run(["git", "init"], cwd=self.repo_dir, check=True)
            print("✓ Initialized git repository")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to initialize git repository: {e}")
            return False
    
    def configure_git(self, username=None, email=None):
        """Configure git user information"""
        try:
            if username:
                subprocess.run(
                    ["git", "config", "user.name", username],
                    cwd=self.repo_dir, check=True
                )
            if email:
                subprocess.run(
                    ["git", "config", "user.email", email],
                    cwd=self.repo_dir, check=True
                )
            print("✓ Git configuration updated")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to configure git: {e}")
            return False
    
    def add_files(self):
        """Add files to git"""
        try:
            subprocess.run(["git", "add", "."], 
                         cwd=self.repo_dir, check=True)
            print("✓ Added files to git")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to add files: {e}")
            return False
    
    def commit(self, message="Initial commit: RAG LaTeX Generator"):
        """Commit changes"""
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_dir, check=True
            )
            print(f"✓ Committed changes: {message}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to commit: {e}")
            return False
    
    def add_remote(self, username, repo_name=None):
        """Add GitHub remote"""
        if repo_name is None:
            repo_name = self.repo_name
        
        remote_url = f"https://github.com/{username}/{repo_name}.git"
        
        try:
            # Check if remote already exists
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✓ Remote 'origin' already exists: {result.stdout.strip()}")
                return True
            
            # Add new remote
            subprocess.run(
                ["git", "remote", "add", "origin", remote_url],
                cwd=self.repo_dir, check=True
            )
            print(f"✓ Added remote: {remote_url}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to add remote: {e}")
            return False
    
    def push(self, branch="main"):
        """Push to GitHub"""
        try:
            # Rename branch to main if needed
            subprocess.run(
                ["git", "branch", "-M", branch],
                cwd=self.repo_dir, check=True
            )
            
            # Push to remote
            subprocess.run(
                ["git", "push", "-u", "origin", branch],
                cwd=self.repo_dir, check=True
            )
            print(f"✓ Pushed to GitHub ({branch} branch)")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to push: {e}")
            print("\nNote: If the repository doesn't exist on GitHub:")
            print("1. Go to https://github.com/new")
            print(f"2. Create a repository named '{self.repo_name}'")
            print("3. Run this script again")
            return False
    
    def create_license(self, license_type="MIT"):
        """Create LICENSE file"""
        mit_license = """MIT License

Copyright (c) 2025 RAG LaTeX Generator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        
        license_file = self.repo_dir / "LICENSE"
        if not license_file.exists():
            with open(license_file, 'w') as f:
                f.write(mit_license)
            print("✓ Created LICENSE file")
        else:
            print("✓ LICENSE file already exists")
    
    def setup(self, github_username, github_email=None):
        """Complete setup process"""
        print("\n" + "="*60)
        print("GitHub Repository Setup")
        print("="*60 + "\n")
        
        # Step 1: Check git
        if not self.check_git_installed():
            return False
        
        # Step 2: Initialize repository
        if not self.init_repository():
            return False
        
        # Step 3: Configure git
        if not self.configure_git(github_username, github_email):
            return False
        
        # Step 4: Create LICENSE
        self.create_license()
        
        # Step 5: Add files
        if not self.add_files():
            return False
        
        # Step 6: Commit
        if not self.commit():
            return False
        
        # Step 7: Add remote
        if not self.add_remote(github_username):
            return False
        
        # Step 8: Push
        print("\nAttempting to push to GitHub...")
        if not self.push():
            print("\n⚠️  Push failed. Please ensure:")
            print(f"   1. Repository exists: https://github.com/{github_username}/{self.repo_name}")
            print("   2. You have proper authentication set up")
            print("   3. You have push permissions")
            return False
        
        print("\n" + "="*60)
        print("✓ Setup complete!")
        print("="*60)
        print(f"\nRepository URL: https://github.com/{github_username}/{self.repo_name}")
        print("\nNext steps:")
        print("1. Visit your repository on GitHub")
        print("2. Add repository description")
        print("3. Add topics/tags")
        print("4. Enable GitHub Pages if desired")
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Setup and push RAG LaTeX Generator to GitHub"
    )
    parser.add_argument(
        "username",
        help="Your GitHub username"
    )
    parser.add_argument(
        "--email",
        help="Your GitHub email (optional)"
    )
    parser.add_argument(
        "--repo-name",
        default="rag-latex-generator",
        help="Repository name (default: rag-latex-generator)"
    )
    
    args = parser.parse_args()
    
    setup = GitHubSetup(repo_name=args.repo_name)
    success = setup.setup(args.username, args.email)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
