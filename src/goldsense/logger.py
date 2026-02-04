from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .models import AnalysisResult


@dataclass
class JsonlLogger:
    path: Path
    _seen_urls: set[str] | None = None

    def __post_init__(self):
        # Load existing URLs from log file for deduplication
        if self._seen_urls is None:
            object.__setattr__(self, '_seen_urls', set())
            if self.path.exists():
                try:
                    with self.path.open("r", encoding="utf-8") as file:
                        for line in file:
                            if line.strip():
                                entry = json.loads(line)
                                url = entry.get("article", {}).get("url")
                                if url:
                                    self._seen_urls.add(url)
                except Exception:
                    pass  # If log file is corrupted, continue with empty set

    def log(self, result: AnalysisResult) -> None:
        # URL-based deduplication
        url = result.article.url
        if url and url in self._seen_urls:
            return  # Skip duplicate URLs
        
        payload = asdict(result)
        payload["logged_at"] = datetime.now(timezone.utc).isoformat()
        payload["article"]["published_at"] = result.article.published_at.isoformat()

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")
        
        # Add to seen URLs
        if url:
            self._seen_urls.add(url)
