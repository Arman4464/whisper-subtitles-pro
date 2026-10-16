"""
GitHub Actions Autonomous Cloud Runner
Dispatches audio transcription & alignment jobs to GitHub Actions cloud runners (Ubuntu/Linux).
Allows transcribing large 1-hour to 5-hour files with zero local PC heating or GPU usage.
"""

import os
import time
import json
import base64
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

class GitHubCloudRunner:
    def __init__(self, repo: str = "Arman4464/whisper-subtitles-pro", token: Optional[str] = None):
        self.repo = repo.strip()
        self.token = (
            token or
            os.environ.get("GITHUB_TOKEN") or
            os.environ.get("GH_TOKEN") or
            ""
        ).strip()
        self.workflow_id = "transcribe.yml"

    def _headers(self) -> Dict[str, str]:
        if not self.token:
            raise RuntimeError(
                "GITHUB_TOKEN is required for cloud execution. Set GITHUB_TOKEN environment variable "
                "or pass --token <your_gh_token>"
            )
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "WhisperSubtitlesPro/1.0"
        }

    def upload_audio_to_release(self, audio_path: str, tag: str = "cloud-input") -> str:
        """
        Uploads audio to a GitHub release asset for cloud workers to fetch.
        Supports up to 2GB audio files.
        """
        filename = os.path.basename(audio_path)
        
        # 1. Get or create release
        get_rel_url = f"https://api.github.com/repos/{self.repo}/releases/tags/{tag}"
        release_id = None
        upload_url = None
        
        try:
            req = urllib.request.Request(get_rel_url, headers=self._headers())
            with urllib.request.urlopen(req, timeout=10) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode())
                    release_id = data.get("id")
                    upload_url = data.get("upload_url", "").split("{")[0]
        except Exception:
            pass

        if not release_id:
            # Create release
            create_url = f"https://api.github.com/repos/{self.repo}/releases"
            payload = {
                "tag_name": tag,
                "name": "Cloud Subtitles Input Cache",
                "body": "Temporary audio storage for autonomous cloud workers",
                "draft": False,
                "prerelease": False
            }
            req = urllib.request.Request(
                create_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=self._headers(),
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as res:
                    if res.status in (200, 201):
                        data = json.loads(res.read().decode())
                        release_id = data.get("id")
                        upload_url = data.get("upload_url", "").split("{")[0]
            except Exception as e:
                raise RuntimeError(f"Failed to create cloud staging release: {e}")

        # 2. Upload asset
        if not upload_url:
            upload_url = f"https://uploads.github.com/repos/{self.repo}/releases/{release_id}/assets"
            
        full_upload_url = f"{upload_url}?name={urllib.parse.quote(filename)}"
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        mime = "audio/wav" if filename.lower().endswith(".wav") else "audio/mpeg"
        headers = self._headers()
        headers["Content-Type"] = mime
        
        req = urllib.request.Request(full_upload_url, data=audio_bytes, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                if res.status in (200, 201):
                    asset_info = json.loads(res.read().decode())
                    return asset_info.get("browser_download_url") or filename
        except urllib.error.HTTPError as e:
            if e.code == 422: # Already exists, return filename
                return filename
            raise RuntimeError(f"Failed to upload audio asset to GitHub: {e}")

        return filename

    def dispatch(
        self,
        audio_name: str,
        model: str = "base",
        task: str = "transcribe",
        output_format: str = "all",
        language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Dispatches workflow run to GitHub Actions.
        """
        url = f"https://api.github.com/repos/{self.repo}/actions/workflows/{self.workflow_id}/dispatches"
        payload = {
            "ref": "main",
            "inputs": {
                "audio_name": audio_name,
                "model": model,
                "task": task,
                "output_format": output_format,
                "language": language
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                if res.status in (200, 204):
                    return {
                        "success": True,
                        "repo": self.repo,
                        "workflow_url": f"https://github.com/{self.repo}/actions",
                        "audio_name": audio_name
                    }
                return {"success": False, "status": res.status}
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            return {"success": False, "error": f"HTTP {e.code}: {err_body}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def poll_latest_run(self, timeout_sec: int = 600) -> Optional[Dict[str, Any]]:
        """
        Polls the workflow run until completion and returns the status.
        """
        runs_url = f"https://api.github.com/repos/{self.repo}/actions/workflows/{self.workflow_id}/runs"
        start_t = time.time()
        
        while time.time() - start_t < timeout_sec:
            try:
                req = urllib.request.Request(runs_url, headers=self._headers())
                with urllib.request.urlopen(req, timeout=10) as res:
                    if res.status == 200:
                        data = json.loads(res.read().decode())
                        runs = data.get("workflow_runs", [])
                        if runs:
                            latest = runs[0]
                            status = latest.get("status")
                            conclusion = latest.get("conclusion")
                            if status == "completed":
                                return {
                                    "completed": True,
                                    "conclusion": conclusion,
                                    "html_url": latest.get("html_url"),
                                    "artifacts_url": latest.get("artifacts_url")
                                }
            except Exception:
                pass
            time.sleep(6)

        return None
