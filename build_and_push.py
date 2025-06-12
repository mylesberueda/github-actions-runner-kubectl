#!/usr/bin/env python3
"""
Docker Build and Push Script for GitHub Actions Runner with kubectl

This script builds the Dockerfile and pushes it to a container registry.
Supports GitHub Container Registry (ghcr.io) and Docker Hub.

Usage:
    python build_and_push.py [options]

Environment Variables:
    REGISTRY_URL: Container registry URL (default: ghcr.io)
    REGISTRY_USERNAME: Registry username
    REGISTRY_PASSWORD: Registry password/token
    IMAGE_NAME: Image name (default: github-actions-runner-kubectl)
    IMAGE_TAG: Image tag (default: latest)
    DOCKERFILE_PATH: Path to Dockerfile (default: ./Dockerfile)
"""

import os
import sys
import argparse
import logging
import subprocess
from typing import Optional, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DockerBuilder:
    """Handles Docker image building and pushing operations."""
    
    def __init__(
        self,
        registry_url: str = "ghcr.io",
        username: Optional[str] = None,
        password: Optional[str] = None,
        image_name: str = "github-actions-runner-kubectl",
        dockerfile_path: str = "./Dockerfile"
    ):
        self.registry_url = registry_url.rstrip('/')
        self.username = username
        self.password = password
        self.image_name = image_name
        self.dockerfile_path = Path(dockerfile_path)
        
        # Validate Dockerfile exists
        if not self.dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found at {self.dockerfile_path}")
    
    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and return the result."""
        logger.info(f"Running: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                logger.info(f"Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            if e.stderr:
                logger.error(f"Error output: {e.stderr.strip()}")
            raise
    
    def login(self) -> bool:
        """Login to the container registry."""
        if not self.username or not self.password:
            logger.warning("No credentials provided, skipping login")
            return False

        try:
            logger.info(f"Logging in to {self.registry_url}")

            # Method 1: Try with --password-stdin (preferred method)
            try:
                login_process = subprocess.Popen(
                    ["docker", "login", self.registry_url, "--username", self.username, "--password-stdin"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Send password to stdin with timeout
                try:
                    stdout, stderr = login_process.communicate(input=self.password + '\n', timeout=30)
                except subprocess.TimeoutExpired:
                    login_process.kill()
                    logger.error("Docker login timed out after 30 seconds")
                    return self._fallback_login()

                if login_process.returncode == 0:
                    logger.info("Successfully logged in to registry")
                    if stdout.strip():
                        logger.info(f"Login output: {stdout.strip()}")
                    return True
                else:
                    logger.warning(f"Standard login failed with return code {login_process.returncode}")
                    if stderr.strip():
                        logger.warning(f"Login error: {stderr.strip()}")
                    return self._fallback_login()

            except Exception as e:
                logger.warning(f"Standard login method failed: {e}")
                return self._fallback_login()

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def _fallback_login(self) -> bool:
        """Fallback login method using environment variable."""
        try:
            logger.info("Trying fallback login method...")

            # Set password as environment variable temporarily
            env = os.environ.copy()
            env['DOCKER_PASSWORD'] = self.password

            # Use echo to pipe password
            echo_process = subprocess.Popen(
                ["echo", self.password],
                stdout=subprocess.PIPE,
                text=True
            )

            login_process = subprocess.Popen(
                ["docker", "login", self.registry_url, "--username", self.username, "--password-stdin"],
                stdin=echo_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            echo_process.stdout.close()
            stdout, stderr = login_process.communicate(timeout=30)

            if login_process.returncode == 0:
                logger.info("Successfully logged in using fallback method")
                return True
            else:
                logger.error(f"Fallback login also failed: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Fallback login error: {e}")
            return False
    
    def build_image(self, tags: List[str], build_args: Optional[dict] = None) -> bool:
        """Build the Docker image with specified tags."""
        try:
            logger.info(f"Building Docker image from {self.dockerfile_path}")
            
            # Construct build command
            command = ["docker", "build"]
            
            # Add build arguments if provided
            if build_args:
                for key, value in build_args.items():
                    command.extend(["--build-arg", f"{key}={value}"])
            
            # Add tags
            for tag in tags:
                command.extend(["-t", tag])
            
            # Add dockerfile and context
            command.extend(["-f", str(self.dockerfile_path), "."])
            
            self.run_command(command)
            logger.info("Docker image built successfully")
            return True
            
        except Exception as e:
            logger.error(f"Build failed: {e}")
            return False
    
    def push_image(self, tags: List[str]) -> bool:
        """Push the Docker image to the registry."""
        try:
            for tag in tags:
                logger.info(f"Pushing image: {tag}")
                self.run_command(["docker", "push", tag])
            
            logger.info("All images pushed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Push failed: {e}")
            return False
    
    def get_full_image_name(self, tag: str) -> str:
        """Get the full image name including registry and namespace."""
        if self.registry_url == "ghcr.io":
            # For GitHub Container Registry, include the username
            if self.username:
                return f"{self.registry_url}/{self.username.lower()}/{self.image_name}:{tag}"
            else:
                return f"{self.registry_url}/{self.image_name}:{tag}"
        else:
            # For Docker Hub and other registries
            if self.username:
                return f"{self.registry_url}/{self.username}/{self.image_name}:{tag}"
            else:
                return f"{self.registry_url}/{self.image_name}:{tag}"


def main():
    """Main function to handle command line arguments and execute build/push."""
    parser = argparse.ArgumentParser(
        description="Build and push Docker image for GitHub Actions Runner with kubectl"
    )
    
    parser.add_argument(
        "--registry-url",
        default=os.getenv("REGISTRY_URL", "ghcr.io"),
        help="Container registry URL (default: ghcr.io)"
    )
    
    parser.add_argument(
        "--username",
        default=os.getenv("REGISTRY_USERNAME"),
        help="Registry username (can also use REGISTRY_USERNAME env var)"
    )
    
    parser.add_argument(
        "--password",
        default=os.getenv("REGISTRY_PASSWORD"),
        help="Registry password/token (can also use REGISTRY_PASSWORD env var)"
    )
    
    parser.add_argument(
        "--image-name",
        default=os.getenv("IMAGE_NAME", "github-actions-runner-kubectl"),
        help="Image name (default: github-actions-runner-kubectl)"
    )
    
    parser.add_argument(
        "--tags",
        nargs="+",
        default=[os.getenv("IMAGE_TAG", "latest")],
        help="Image tags (default: latest)"
    )
    
    parser.add_argument(
        "--dockerfile",
        default=os.getenv("DOCKERFILE_PATH", "./Dockerfile"),
        help="Path to Dockerfile (default: ./Dockerfile)"
    )
    
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Build only, don't push to registry"
    )
    
    parser.add_argument(
        "--build-args",
        nargs="*",
        help="Build arguments in KEY=VALUE format"
    )
    
    args = parser.parse_args()
    
    # Parse build arguments
    build_args = {}
    if args.build_args:
        for arg in args.build_args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                build_args[key] = value
            else:
                logger.warning(f"Invalid build arg format: {arg}")
    
    try:
        # Initialize builder
        builder = DockerBuilder(
            registry_url=args.registry_url,
            username=args.username,
            password=args.password,
            image_name=args.image_name,
            dockerfile_path=args.dockerfile
        )
        
        # Generate full image names with tags
        full_tags = [builder.get_full_image_name(tag) for tag in args.tags]
        
        logger.info(f"Building image(s): {', '.join(full_tags)}")
        
        # Build the image
        if not builder.build_image(full_tags, build_args):
            sys.exit(1)
        
        # Push the image if not disabled
        if not args.no_push:
            login_success = builder.login()
            if not login_success:
                logger.warning("Login failed, attempting to push without authentication")
                logger.info("Note: If push fails, try logging in manually with: docker login " + args.registry_url)

            if not builder.push_image(full_tags):
                if not login_success:
                    logger.error("Push failed. Try logging in manually first:")
                    logger.error(f"  docker login {args.registry_url} -u {args.username}")
                    logger.error("  Then run this script again")
                sys.exit(1)
        else:
            logger.info("Skipping push (--no-push specified)")
        
        logger.info("Build and push completed successfully!")
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
