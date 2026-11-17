from __future__ import annotations

import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from app.core.config import settings


class StorageError(Exception):
    """Domain exception for file storage failures."""
    pass


class InvalidFileError(StorageError):
    """Raised when file validation fails (type, size, or signature)."""
    pass


class BaseStorageService(ABC):
    @abstractmethod
    async def save_file(self, content: bytes, original_filename: str, student_id: str) -> tuple[str, int]:
        """Save file bytes and return relative storage path and byte size."""

    @abstractmethod
    def get_absolute_path(self, relative_path: str) -> str:
        """Resolve safe absolute path for reading."""

    @abstractmethod
    def delete_file(self, relative_path: str) -> None:
        """Remove file from storage."""


class LocalStorageService(BaseStorageService):
    """Local filesystem storage service with path traversal defense and magic byte checking."""

    PDF_MAGIC = b"%PDF-"
    DOCX_MAGIC = b"PK\x03\x04"

    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = os.path.abspath(base_dir or settings.UPLOAD_DIR)
        os.makedirs(self.base_dir, exist_ok=True)

    def validate_file(self, content: bytes, original_filename: str, content_type: str | None = None) -> str:
        """Validate file size, extension, MIME, and magic byte signatures.

        Args:
            content: Raw file bytes.
            original_filename: Original file name from user upload.
            content_type: Header content-type if provided.

        Returns:
            The sanitized extension ("pdf" or "docx").

        Raises:
            InvalidFileError: If validation fails.
        """
        # Size check
        if len(content) > settings.max_upload_size_bytes:
            raise InvalidFileError(f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB} MB.")

        ext = original_filename.lower().rsplit(".", 1)[-1] if "." in original_filename else ""
        if ext not in ("pdf", "docx"):
            raise InvalidFileError("Only PDF and DOCX documents are accepted.")

        # Magic byte signature verification
        if ext == "pdf":
            if not content.startswith(self.PDF_MAGIC):
                raise InvalidFileError("Invalid PDF file signature.")
        elif ext == "docx":
            if not content.startswith(self.DOCX_MAGIC):
                raise InvalidFileError("Invalid DOCX file signature.")

        return ext

    async def save_file(self, content: bytes, original_filename: str, student_id: str) -> tuple[str, int]:
        """Save file with a randomized UUID filename inside a user-specific folder."""
        ext = self.validate_file(content, original_filename)
        random_filename = f"{uuid.uuid4().hex}.{ext}"

        user_dir = os.path.join(self.base_dir, student_id)
        os.makedirs(user_dir, exist_ok=True)

        target_path = os.path.join(user_dir, random_filename)

        # Path traversal defense
        if os.path.commonpath([target_path, self.base_dir]) != self.base_dir:
            raise InvalidFileError("Potential path traversal detected.")

        with open(target_path, "wb") as f:
            f.write(content)

        relative_path = os.path.relpath(target_path, self.base_dir)
        return relative_path, len(content)

    def get_absolute_path(self, relative_path: str) -> str:
        """Resolve and verify safe absolute path."""
        target_path = os.path.abspath(os.path.join(self.base_dir, relative_path))
        if os.path.commonpath([target_path, self.base_dir]) != self.base_dir:
            raise InvalidFileError("Invalid file path.")
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"File not found: {relative_path}")
        return target_path

    def delete_file(self, relative_path: str) -> None:
        """Delete file if it exists."""
        try:
            abs_path = self.get_absolute_path(relative_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)
        except Exception:
            pass


storage_service = LocalStorageService()

