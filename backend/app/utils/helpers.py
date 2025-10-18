from datetime import datetime
from typing import Any
import hashlib


def get_current_timestamp() -> str:
    """
    获取当前UTC时间的ISO格式时间戳
    
    Returns:
        ISO格式时间戳字符串
    """
    return datetime.utcnow().isoformat() + "Z"


def parse_iso_timestamp(timestamp_str: str) -> datetime:
    """
    解析ISO格式时间戳
    
    Args:
        timestamp_str: ISO格式时间戳字符串
        
    Returns:
        datetime对象
    """
    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    对字符串进行哈希
    
    Args:
        text: 待哈希的字符串
        algorithm: 哈希算法（默认sha256）
        
    Returns:
        十六进制哈希值
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode())
    return hash_obj.hexdigest()


def format_score(score: float, precision: int = 6) -> str:
    """
    格式化分数
    
    Args:
        score: 分数
        precision: 小数位数
        
    Returns:
        格式化后的分数字符串
    """
    return f"{score:.{precision}f}"

