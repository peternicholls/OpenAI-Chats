#!/usr/bin/env python3
"""Analyze OpenAI export structure for planning"""
import json

ARCHIVE_DIR = "6a46cf212e33de2339fe70a219a979b44d35de684e8b961a5e3b73077d3caef5-2026-01-26-08-54-37-28ec05edc89840ebbb963f264ef55875"

with open(f"{ARCHIVE_DIR}/conversations.json") as f:
    data = json.load(f)

conv = data[0]
print("=== Top-level conversation keys ===")
print(list(conv.keys()))

print("\n=== Sample values ===")
for key in conv:
    val = conv[key]
    if key == 'mapping':
        print(f"  {key}: dict with {len(val)} nodes (message tree)")
    elif isinstance(val, dict):
        print(f"  {key}: dict")
    elif isinstance(val, list):
        print(f"  {key}: list of {len(val)} items")
    else:
        print(f"  {key}: {type(val).__name__} = {repr(val)[:80]}")

# Analyze mapping/message structure
print("\n=== Message node structure ===")
mapping = conv['mapping']
for node_id, node in list(mapping.items())[:3]:
    print(f"\nNode: {node_id[:20]}...")
    print(f"  keys: {list(node.keys())}")
    if node.get('message'):
        msg = node['message']
        print(f"  message.keys: {list(msg.keys())}")
        print(f"  author.role: {msg.get('author', {}).get('role')}")
        content = msg.get('content', {})
        print(f"  content.type: {content.get('content_type')}")
        parts = content.get('parts', [])
        if parts and isinstance(parts[0], str):
            print(f"  content.parts[0]: {parts[0][:60]}..." if len(parts[0]) > 60 else f"  content.parts[0]: {parts[0]}")
