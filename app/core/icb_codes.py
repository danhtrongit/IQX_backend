"""ICB (Industry Classification Benchmark) codes utility."""

import json
from pathlib import Path
from typing import Dict, Optional, List
from functools import lru_cache


@lru_cache(maxsize=1)
def load_icb_codes() -> List[Dict]:
    """Load ICB codes from JSON file."""
    file_path = Path(__file__).parent.parent.parent / "data" / "icb_codes.json"
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_icb_mapping() -> Dict[str, Dict]:
    """
    Get ICB code to sector mapping.
    
    Returns:
        Dict with code as key and dict with en_sector, vi_sector, level as value.
        Includes both original codes (like "0001") and numeric versions (like "1").
    """
    codes = load_icb_codes()
    mapping = {}
    
    for item in codes:
        code = item["code"]
        data = {
            "en_sector": item["en_sector"],
            "vi_sector": item["vi_sector"],
            "level": item["level"]
        }
        # Add original code
        mapping[code] = data
        # Also add numeric version (strip leading zeros)
        if code != "OTHER":
            numeric_code = str(int(code))
            if numeric_code != code:
                mapping[numeric_code] = data
    
    return mapping


def get_sector_name(code: int | str, lang: str = "vi") -> Optional[str]:
    """
    Get sector name by ICB code.
    
    Args:
        code: ICB code (int or str)
        lang: Language - 'vi' for Vietnamese, 'en' for English
    
    Returns:
        Sector name or None if not found
    """
    mapping = get_icb_mapping()
    code_str = str(code)
    
    if code_str in mapping:
        key = "vi_sector" if lang == "vi" else "en_sector"
        return mapping[code_str][key]
    
    return None


def get_level1_sectors() -> List[Dict]:
    """Get all level 1 (top level) sectors."""
    codes = load_icb_codes()
    return [item for item in codes if item["level"] == 1]


def get_level2_sectors() -> List[Dict]:
    """Get all level 2 sectors."""
    codes = load_icb_codes()
    return [item for item in codes if item["level"] == 2]


# Quick access mapping
ICB_MAPPING = get_icb_mapping()
