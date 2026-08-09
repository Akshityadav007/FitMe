from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar, Protocol
from uuid import uuid4


class ObjectStorage(Protocol):
    def save(self, *, data: bytes, content_type: str) -> str: ...
    def open(self, *, key: str) -> bytes: ...
    def url(self, *, key: str) -> str: ...


class LocalObjectStorage:
    """Local filesystem storage. Keys are random UUIDs with an extension
    derived from the content type. Used for local development; swap in a
    cloud-backed implementation for production."""

    _EXTENSIONS: ClassVar[dict[str, str]] = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    def __init__(self, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        return self._base_dir / key

    def save(self, *, data: bytes, content_type: str) -> str:
        key = f"{uuid4().hex}{self._EXTENSIONS.get(content_type, '')}"
        self._path_for(key).write_bytes(data)
        return key

    def open(self, *, key: str) -> bytes:
        path = self._path_for(key)
        if not path.is_file():
            raise FileNotFoundError(f"Object not found: {key}")
        return path.read_bytes()

    def url(self, *, key: str) -> str:
        return f"/uploads/{key}"


def get_object_storage() -> ObjectStorage:
    from app.core.config import get_settings

    return LocalObjectStorage(get_settings().upload_dir)


class SecureUploadValidator:
    """Validates uploads before they reach storage. Guards against unsafe
    content types and oversized payloads."""

    _ALLOWED: ClassVar[set[str]] = {"image/jpeg", "image/png", "image/webp"}

    def __init__(self, max_bytes: int) -> None:
        self._max_bytes = max_bytes

    def validate(self, *, content_type: str, data: bytes) -> None:
        if content_type not in self._ALLOWED:
            raise ValueError(f"Unsupported content type: {content_type}")
        if len(data) == 0:
            raise ValueError("Uploaded file is empty")
        if len(data) > self._max_bytes:
            raise ValueError(f"Upload exceeds maximum size of {self._max_bytes} bytes")


def is_url_within_uploads(key: str) -> bool:
    return os.path.normpath(key) == key and not key.startswith("..")
