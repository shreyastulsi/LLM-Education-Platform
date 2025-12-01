import os
from typing import Optional

from .testing import create_db_from_pdf, create_db_from_youtube_video_url
from .supabase_client import latest_source, download_to_tempfile


def load_db_for_user(user_id: str):
    """Load a vector store for the latest source of this user."""
    src = latest_source(user_id)
    if not src:
        raise RuntimeError("No source found. Upload a PDF or provide a YouTube link.")

    if src.get("source_type") == "youtube" and src.get("youtube_url"):
        return create_db_from_youtube_video_url(src["youtube_url"])

    if src.get("source_type") == "pdf" and src.get("storage_path"):
        temp_path = download_to_tempfile(src["storage_path"])
        return create_db_from_pdf(temp_path)

    raise RuntimeError("Unsupported source configuration. Please upload again.")
