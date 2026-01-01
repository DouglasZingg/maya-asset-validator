import json
import os
import getpass
import socket
from datetime import datetime

import maya.cmds as cmds


def build_report(results):
    """
    Build a report dict suitable for JSON export.

    Args:
        results (list[dict]): items like {"level","node","message"}

    Returns:
        dict: report payload
    """
    scene_path = cmds.file(q=True, sn=True) or ""
    scene_name = os.path.basename(scene_path) if scene_path else "untitled"
    maya_version = cmds.about(version=True)

    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for r in results or []:
        lvl = r.get("level", "INFO")
        if lvl not in counts:
            counts[lvl] = 0
        counts[lvl] += 1

    report = {
        "meta": {
            "tool": "maya-asset-validator",
            "scene_name": scene_name,
            "scene_path": scene_path,
            "maya_version": maya_version,
            "user": getpass.getuser(),
            "machine": socket.gethostname(),
            "timestamp_local": datetime.now().isoformat(timespec="seconds"),
        },
        "summary": {
            "total": len(results or []),
            "counts": counts,
        },
        "results": results or [],
    }
    return report


def export_report_json(filepath, report_dict):
    """
    Write report_dict to filepath as JSON.
    """
    folder = os.path.dirname(filepath)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, ensure_ascii=False)


def export_report_txt(filepath, report_dict):
    """
    Write a human-readable TXT report.
    """
    folder = os.path.dirname(filepath)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    meta = report_dict.get("meta", {})
    summary = report_dict.get("summary", {})
    counts = (summary.get("counts") or {})
    results = report_dict.get("results") or []

    lines = []
    lines.append("Maya Asset Validator Report")
    lines.append("=" * 30)
    lines.append(f"Scene: {meta.get('scene_name', '')}")
    lines.append(f"Scene Path: {meta.get('scene_path', '')}")
    lines.append(f"Maya Version: {meta.get('maya_version', '')}")
    lines.append(f"User: {meta.get('user', '')}")
    lines.append(f"Machine: {meta.get('machine', '')}")
    lines.append(f"Timestamp: {meta.get('timestamp_local', '')}")
    lines.append("")
    lines.append("Summary")
    lines.append("-" * 30)
    lines.append(f"Total Issues: {summary.get('total', 0)}")
    lines.append(f"ERROR: {counts.get('ERROR', 0)}")
    lines.append(f"WARNING: {counts.get('WARNING', 0)}")
    lines.append(f"INFO: {counts.get('INFO', 0)}")
    lines.append("")
    lines.append("Details")
    lines.append("-" * 30)

    for r in results:
        lvl = r.get("level", "INFO")
        node = r.get("node", "")
        msg = r.get("message", "")
        lines.append(f"[{lvl}] {node} — {msg}")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
