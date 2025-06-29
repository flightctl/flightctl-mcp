import os
import shutil
import subprocess
import tempfile
import urllib.parse


class FlightctlCLI:
    def __init__(self, api_url: str, arch: str = "amd64", os_name: str = "linux"):
        self.api_url = api_url.rstrip("/")
        self.arch = arch
        self.os_name = os_name
        self.install_dir = os.environ.get("FLIGHTCTL_CLI_DIR", os.path.expanduser("~/.local/bin"))
        self.cli_path = os.path.join(self.install_dir, "flightctl")

    def download(self) -> None:
        """
        Downloads and installs the flightctl CLI matching the domain of the API server.
        Installs to a user-writable directory (default: ~/.local/bin).
        If CLI is already available system-wide, skips download.
        """
        # Check if flightctl is already available system-wide
        existing_cli = shutil.which("flightctl")
        if existing_cli:
            print("flightctl CLI already available system-wide, skipping download")
            self.cli_path = existing_cli
            return

        domain = urllib.parse.urlparse(self.api_url).netloc
        domain_prefix = domain.split("api.", 1)[-1]
        cli_url = f"https://cli-artifacts.{domain_prefix}/{self.arch}/{self.os_name}/flightctl-{self.os_name}-{self.arch}.tar.gz"

        with tempfile.TemporaryDirectory() as tmpdir:
            tar_path = os.path.join(tmpdir, "flightctl.tar.gz")
            subprocess.run(["curl", "-kfLo", tar_path, cli_url], check=True)
            subprocess.run(["tar", "-xvf", tar_path, "-C", tmpdir], check=True)

            extracted_path = os.path.join(tmpdir, "flightctl")
            if not os.path.isfile(extracted_path):
                raise RuntimeError("Failed to extract flightctl binary")

            os.makedirs(self.install_dir, exist_ok=True)
            shutil.move(extracted_path, self.cli_path)
            os.chmod(self.cli_path, 0o755)

            os.environ["PATH"] = f"{self.install_dir}:{os.environ.get('PATH', '')}"
