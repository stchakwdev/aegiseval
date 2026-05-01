from __future__ import annotations

from pydantic import BaseModel


class ExploitFinding(BaseModel):
    title: str
    exploit_found: bool
    severity: str
    issues: list[str]
    transcript: list[str]
