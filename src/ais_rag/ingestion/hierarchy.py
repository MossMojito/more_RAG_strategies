from pathlib import Path
from ..config import FILE_TO_SPORT_MAPPING

def create_parent_child_data(filepath: Path):
    """
    Create Parent documents (Full Content) and Child documents (Sport-Specific splits)
    strictly for Multi-Sport packages (PLAY SPORTS, PLAY ULTIMATE).
    """
    filename = filepath.name
    if filename not in FILE_TO_SPORT_MAPPING:
        return None, []
    
    mapping = FILE_TO_SPORT_MAPPING[filename]
    if not mapping["is_multi_sport"]:
        return None, []

    # Read content
    with open(filepath, 'r', encoding='utf-8') as f:
        full_content = f.read()

    package_name = filename.replace("final_", "").replace("_clean.md", "")
    package_name_clean = package_name.replace("_", " ") # For display
    
    parent_id = f"{package_name}_parent"
    
    # 1. Create Parent (Full File)
    parent_doc = {
        "id": parent_id,
        "package": package_name,
        "full_content": full_content,
        "sports": mapping["sports"]
    }

    # 2. Create Children (Manual Logic from original notebook)
    children = []
    
    # Emoji map just for generating the content string
    emoji_map = {
        "EPL": "⚽", "NBA": "🏀", "NFL": "🏈", "TENNIS": "🎾", "GOLF": "⛳"
    }

    for sport in mapping["sports"]:
        emoji = emoji_map.get(sport, "🏆")
        other_sports = [s for s in mapping["sports"] if s != sport]
        
        # Semantic Child Content
        child_content = f"""แพ็กเกจ {package_name_clean} (แพ็กเกจรวมหลายกีฬา)

🎯 กีฬาหลัก: {emoji} {sport}

ดู {sport} ได้ครบทุกรายการบน AIS PLAY

⭐ รับชม - ดูกีฬาอื่นได้ด้วย:
{', '.join(other_sports)}

รายละเอียดเพิ่มเติมใน {package_name_clean}"""

        child_id = f"multi_child_{package_name}_{sport}"
        
        children.append({
            "chunk_id": child_id,
            "content": child_content,
            "metadata": {
                "parent_id": parent_id,
                "package": package_name,
                "sport": sport,
                "is_multi_sport": True,
                "all_sports": mapping["sports"],
                "source_file": filename,
                "type": "child"
            }
        })

    return parent_doc, children
