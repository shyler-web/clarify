from __future__ import annotations

import httpx

from paydown.agent import RefactorResult
from paydown.config import ConfigError, get_env

_GITHUB_API = "https://api.github.com"


def _branch_exists(headers: dict, repo_slug: str, branch: str) -> bool:
    url = f"{_GITHUB_API}/repos/{repo_slug}/branches/{branch}"
    resp = httpx.get(url, headers=headers)
    return resp.status_code == 200


def _base_sha(headers: dict, repo_slug: str, base: str) -> str:
    url = f"{_GITHUB_API}/repos/{repo_slug}/git/ref/heads/{base}"
    resp = httpx.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["object"]["sha"]


def _create_branch(headers: dict, repo_slug: str, branch: str, base: str) -> None:
    if _branch_exists(headers, repo_slug, branch):
        return
    sha = _base_sha(headers, repo_slug, base)
    url = f"{_GITHUB_API}/repos/{repo_slug}/git/refs"
    resp = httpx.post(
        url,
        headers=headers,
        json={"ref": f"refs/heads/{branch}", "sha": sha},
    )
    resp.raise_for_status()


def _get_sha(headers: dict, repo_slug: str, branch: str, path: str) -> str | None:
    url = f"{_GITHUB_API}/repos/{repo_slug}/contents/{path}?ref={branch}"
    resp = httpx.get(url, headers=headers)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()["sha"]


def _commit_content(headers: dict, repo_slug: str, branch: str, path: str, content: str) -> None:
    url = f"{_GITHUB_API}/repos/{repo_slug}/contents/{path}"
    payload = {
        "message": f"refactor: {path}",
        "content": _b64(content),
        "branch": branch,
    }
    sha = _get_sha(headers, repo_slug, branch, path)
    if sha:
        payload["sha"] = sha
    resp = httpx.put(url, headers=headers, json=payload)
    resp.raise_for_status()


def _b64(data: str) -> str:
    import base64

    return base64.b64encode(data.encode()).decode()


def _open_pr(headers: dict, repo_slug: str, branch: str, base: str, refactor: RefactorResult) -> str:
    title = f"refactor: {refactor.path}"
    body = (
        f"Refactored `{refactor.path}` to simplify while preserving behavior.\n\n"
        f"**Before**: original source\n"
        f"**After**: `{refactor.path}`\n"
        f"**Tests passing**: {refactor.test_passes}\n\n"
        f"### Note\n{refactor.explanation}\n"
    )
    url = f"{_GITHUB_API}/repos/{repo_slug}/pulls"
    resp = httpx.post(
        url,
        headers=headers,
        json={
            "title": title,
            "head": branch,
            "base": base,
            "body": body,
        },
    )
    resp.raise_for_status()
    return resp.json()["html_url"]


def open_pr(
    repo_slug: str, branch: str, refactor: RefactorResult, base: str = "main"
) -> str:
    token = get_env("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    _create_branch(headers, repo_slug, branch, base)
    _commit_content(
        headers, repo_slug, branch, refactor.path, refactor.refactored_source
    )
    return _open_pr(headers, repo_slug, branch, base, refactor)