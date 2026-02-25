"""Generate test data fixtures for chatgpt_archive tests.

Creates sample conversations with varying sizes for performance testing.

Usage:
    python tests/fixtures/generate_test_data.py
"""

import json
import time
import zipfile
from pathlib import Path


def generate_conversation(conv_id: str, title: str, message_count: int, start_time: float = 1700000000.0) -> dict:
    """Generate a conversation with the specified number of messages."""
    mapping = {}
    prev_id = None
    children_map: dict[str, list[str]] = {}

    for i in range(message_count):
        msg_id = f"msg-{conv_id}-{i:04d}"
        role = "user" if i % 2 == 0 else "assistant"

        if prev_id:
            children_map.setdefault(prev_id, []).append(msg_id)

        mapping[msg_id] = {
            "id": msg_id,
            "message": {
                "id": msg_id,
                "author": {"role": role},
                "content": {
                    "parts": [f"This is message {i} in conversation {title}. " * 5],
                    "content_type": "text",
                },
                "create_time": start_time + i * 60,
            },
            "parent": prev_id,
            "children": [],
        }
        prev_id = msg_id

    # Wire up children
    for parent_id, children in children_map.items():
        mapping[parent_id]["children"] = children

    return {
        "id": conv_id,
        "title": title,
        "create_time": start_time,
        "update_time": start_time + message_count * 60,
        "mapping": mapping,
    }


def generate_test_data(output_dir: Path) -> None:
    """Generate test fixture files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    sizes = [
        ("small", 10),
        ("medium", 100),
        ("large", 1000),
    ]

    for size_name, message_count in sizes:
        conv_id = f"perf-test-{size_name}"
        title = f"Performance Test ({message_count} messages)"
        start_time = 1700000000.0

        conv = generate_conversation(conv_id, title, message_count, start_time)

        output_file = output_dir / f"conversation_{size_name}.json"
        output_file.write_text(json.dumps([conv], indent=2))
        print(f"Generated: {output_file} ({message_count} messages)")

    # Generate a full archive with multiple conversations
    conversations = []
    for i in range(3):
        conv_id = f"archive-conv-{i:03d}"
        title = f"Archive Conversation {i + 1}"
        message_count = 10 + i * 5
        start_time = 1700000000.0 + i * 86400

        conversations.append(
            generate_conversation(conv_id, title, message_count, start_time)
        )

    archive_dir = output_dir / "generated_archive"
    archive_dir.mkdir(exist_ok=True)

    (archive_dir / "conversations.json").write_text(json.dumps(conversations, indent=2))
    (archive_dir / "user.json").write_text(
        json.dumps({"id": "generated-user", "email": "generated@example.com"})
    )

    # Create ZIP
    zip_path = output_dir / "generated_archive.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in archive_dir.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(archive_dir))

    print(f"Generated: {zip_path}")


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "generated"
    generate_test_data(output_dir)
    print("Done!")
