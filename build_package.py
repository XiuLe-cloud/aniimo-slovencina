"""Compatibility token grammar used by pipeline.qa; see build_text_data.py for building."""
import re
TOKEN=re.compile(r'<[^>\n]+>|\{[^{}]*\}|#[A-Za-z_][A-Za-z0-9_]*#|\$[A-Za-z_][A-Za-z0-9_]*|%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?[sdifouxXeEgGc%]|\\[nrt]|\r\n|\r|\n')
