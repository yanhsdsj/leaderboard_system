import hmac
import hashlib
from typing import Dict

# 服务器端密钥（实际使用时应从环境变量读取）
SECRET_KEY = "ZeroGen-Leaderboard-Secret"


def generate_signature(data: Dict, secret: str = SECRET_KEY) -> str:
    """
    生成HMAC-SHA256签名
    
    Args:
        data: 包含学生信息和提交数据的字典
        secret: 密钥
        
    Returns:
        十六进制签名字符串
    """
    # 构造签名消息
    msg = (
        f"{data['student_info']['student_id']}:"
        f"{data['assignment_id']}:"
        f"{data['submission_data']['metrics']['MAE']}:"
        f"{data['submission_data']['metrics']['MSE']}:"
        f"{data['submission_data']['metrics']['RMSE']}:"
        f"{data['submission_data']['metrics']['Prediction_Time']}:"
        f"{data['submission_data']['timestamp']}"
    )
    
    # 生成HMAC签名
    signature = hmac.new(
        secret.encode(),
        msg.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def verify_signature(data: Dict, signature: str, secret: str = SECRET_KEY) -> bool:
    """
    验证签名
    
    Args:
        data: 提交数据
        signature: 待验证的签名
        secret: 密钥
        
    Returns:
        签名是否有效
    """
    expected_signature = generate_signature(data, secret)
    return hmac.compare_digest(expected_signature, signature)


def verify_client_signature(student_id: str, assignment_id: str, metrics: Dict, signature: str, secret: str = SECRET_KEY) -> bool:
    """
    验证客户端提交的签名
    
    Args:
        student_id: 学生ID
        assignment_id: 作业ID
        metrics: 评估指标
        signature: 待验证的签名
        secret: 密钥
        
    Returns:
        签名是否有效
    """
    # 构造客户端签名消息
    msg = (
        f"{student_id}:"
        f"{assignment_id}:"
        f"{metrics['MAE']}:"
        f"{metrics['MSE']}:"
        f"{metrics['RMSE']}:"
        f"{metrics['Prediction_Time']}"
    )
    
    # 生成期望的签名
    expected_signature = hmac.new(
        secret.encode(),
        msg.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

