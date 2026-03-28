from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProcessRecord:
    pid: int
    ppid: int
    etime: str
    elapsed_seconds: int
    cpu_percent: float
    mem_percent: float
    rss_kb: int
    command: str
    args: str
    family: str = "other"
    role: str = "unknown"
    classification: str = "UNCLASSIFIED"
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StorageRecord:
    label: str
    path: str
    family: str
    classification: str
    size_bytes: int
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CleanupAction:
    target: str
    target_type: str
    family: str
    classification: str
    result: str
    bytes_reclaimed: int
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DockerInventory:
    engine_available: bool
    info: Optional[Dict[str, Any]] = None
    containers: List[Dict[str, Any]] = field(default_factory=list)
    dangling_images: List[Dict[str, Any]] = field(default_factory=list)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    networks: List[Dict[str, Any]] = field(default_factory=list)
    timed_out_commands: List[str] = field(default_factory=list)
    raw_text: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScanSnapshot:
    run_id: str
    started_at: str
    finished_at: str
    mode: str
    host_disk_total_bytes: int
    host_disk_used_bytes: int
    host_disk_free_bytes: int
    processes: List[ProcessRecord]
    storage_records: List[StorageRecord]
    docker_inventory: DockerInventory
    protected_items: List[StorageRecord]
    manual_review_items: List[StorageRecord]

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        return payload


@dataclass
class CleanupReport:
    run_id: str
    started_at: str
    finished_at: str
    mode: str
    dry_run: bool
    storage_before_bytes: int
    storage_after_bytes: int
    storage_reclaimed_bytes: int
    memory_before_estimate_mb: float
    memory_after_estimate_mb: float
    memory_reclaimed_estimate_mb: float
    processes_scanned: int
    processes_trimmed: int
    objects_pruned: int
    protected_items: List[Dict[str, Any]]
    manual_review_items: List[Dict[str, Any]]
    family_summaries: Dict[str, Dict[str, Any]]
    actions: List[CleanupAction]
    snapshot: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "mode": self.mode,
            "dry_run": self.dry_run,
            "storage_before_bytes": self.storage_before_bytes,
            "storage_after_bytes": self.storage_after_bytes,
            "storage_reclaimed_bytes": self.storage_reclaimed_bytes,
            "memory_before_estimate_mb": self.memory_before_estimate_mb,
            "memory_after_estimate_mb": self.memory_after_estimate_mb,
            "memory_reclaimed_estimate_mb": self.memory_reclaimed_estimate_mb,
            "processes_scanned": self.processes_scanned,
            "processes_trimmed": self.processes_trimmed,
            "objects_pruned": self.objects_pruned,
            "protected_items": self.protected_items,
            "manual_review_items": self.manual_review_items,
            "family_summaries": self.family_summaries,
            "actions": [action.to_dict() for action in self.actions],
            "snapshot": self.snapshot,
        }
