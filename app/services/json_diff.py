from typing import Dict, Any

def deep_diff(obj1: Dict, obj2: Dict, path: str = "") -> Dict:
    """
    Сравнивает два словаря, возвращает структуру с added, removed, changed.
    """
    diff = {"added": {}, "removed": {}, "changed": {}}
    keys1 = set(obj1.keys())
    keys2 = set(obj2.keys())

    for key in keys1 - keys2:
        full_path = f"{path}.{key}" if path else key
        diff["removed"][full_path] = obj1[key]

    for key in keys2 - keys1:
        full_path = f"{path}.{key}" if path else key
        diff["added"][full_path] = obj2[key]

    for key in keys1 & keys2:
        full_path = f"{path}.{key}" if path else key
        if isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
            sub_diff = deep_diff(obj1[key], obj2[key], full_path)
            # объединяем поддиффы
            diff["added"].update(sub_diff["added"])
            diff["removed"].update(sub_diff["removed"])
            diff["changed"].update(sub_diff["changed"])
        elif obj1[key] != obj2[key]:
            diff["changed"][full_path] = {"old": obj1[key], "new": obj2[key]}

    return diff