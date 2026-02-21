import dpath.util

def get_value_by_path(data: dict, path: str):
    """Извлечение значения по точечному пути"""
    try:
        return dpath.util.get(data, path, separator=".")
    except KeyError:
        return None

def set_value_by_path(data: dict, path: str, value):
    """Установка значения по пути, создаёт промежуточные ключи"""
    dpath.util.new(data, path, value, separator=".")
    return data

def delete_value_by_path(data: dict, path: str):
    """Удаление ключа по пути"""
    try:
        dpath.util.delete(data, path, separator=".")
    except KeyError:
        pass
    return data