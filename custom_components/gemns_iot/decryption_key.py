"""Parse decryption keys entered during setup."""

import re


def parse_decryption_key(value: str) -> str:
    """Convert sixteen space-separated decimal bytes to stored hex."""
    if re.fullmatch(r"[0-9]{1,3}( [0-9]{1,3}){15}", value) is None:
        raise ValueError("Expected sixteen decimal bytes separated by single spaces")
    return bytes(int(number) for number in value.split(" ")).hex()
