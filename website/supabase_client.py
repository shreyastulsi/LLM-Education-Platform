import os
import uuid
import tempfile
from typing import Optional, Dict, Any, List

from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET = "uploads"

_client: Optional[Client] = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise EnvironmentError("SUPABASE_URL or SUPABASE_KEY missing. Add them to .env")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def upload_bytes(user_id: str, filename: str, data: bytes) -> str:
    """Upload bytes to storage and return the storage path."""
    client = get_client()
    key = f"{user_id}/{uuid.uuid4()}-{filename}"
    client.storage.from_(BUCKET).upload(key, data, {"upsert": True})
    return key


def download_to_tempfile(path: str) -> str:
    """Download a storage object to a temp file and return the path."""
    client = get_client()
    content = client.storage.from_(BUCKET).download(path)
    fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(path)[1] or ".pdf")
    with os.fdopen(fd, "wb") as f:
        f.write(content)
    return temp_path


def record_source(user_id: str, source_type: str, storage_path: Optional[str] = None, youtube_url: Optional[str] = None) -> Dict[str, Any]:
    """Insert a source row and return it."""
    client = get_client()
    row = {
        "user_id": user_id,
        "source_type": source_type,
        "storage_path": storage_path,
        "youtube_url": youtube_url,
    }
    res = client.table("sources").insert(row).execute()
    return res.data[0] if res.data else row


def latest_source(user_id: str) -> Optional[Dict[str, Any]]:
    client = get_client()
    res = (
        client.table("sources")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if res.data:
        return res.data[0]
    return None


def save_test_result(user_id: str, main_score: Optional[int], side_score: Optional[int], missed_topics: str) -> None:
    client = get_client()
    client.table("test_results").insert(
        {
            "user_id": user_id,
            "main_score": main_score,
            "side_score": side_score,
            "missed_topics": missed_topics,
        }
    ).execute()


def fetch_test_results(user_id: str) -> List[Dict[str, Any]]:
    client = get_client()
    res = client.table("test_results").select("*").eq("user_id", user_id).execute()
    return res.data or []
