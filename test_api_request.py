#!/usr/bin/env python3
"""
API请求测试脚本
用于测试排行榜系统的提交接口
"""

import requests
import hashlib
import json
from pathlib import Path

# ==================== 配置区 ====================
API_URL = "http://localhost:8000/api/submit"

# 学生信息
STUDENT_INFO = {
    "student_id": "2021001234",
    "name": "张三",
    "nickname": "代码小能手"  # 可选
}

# 作业编号
ASSIGNMENT_ID = "01"

# 评估指标
METRICS = {
    "MAE": 0.1234,
    "MSE": 0.5678,
    "RMSE": 0.7536,
    "Prediction_Time": 12.34
}

# evaluate.py文件路径
EVALUATE_FILE = "evaluate.py"

# ================================================


def compute_file_md5(filepath):
    """计算文件的MD5哈希值"""
    md5_hash = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except FileNotFoundError:
        print(f"❌ 错误: 文件 {filepath} 不存在")
        return None


def send_request(url, data):
    """发送POST请求"""
    try:
        response = requests.post(
            url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        return response
    except requests.exceptions.ConnectionError:
        print("❌ 错误: 无法连接到服务器，请确保后端服务正在运行")
        return None
    except requests.exceptions.Timeout:
        print("❌ 错误: 请求超时")
        return None
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None


def print_response(response):
    """格式化打印响应"""
    print("\n" + "=" * 60)
    print(f"状态码: {response.status_code}")
    print("=" * 60)
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    
    print("=" * 60)


def main():
    print("=" * 60)
    print("排行榜系统 - API请求测试")
    print("=" * 60)
    
    # 1. 计算MD5
    print("\n📝 步骤1: 计算evaluate.py的MD5...")
    md5_value = compute_file_md5(EVALUATE_FILE)
    
    if md5_value is None:
        print(f"⚠️  将使用预设MD5值")
        md5_value = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
    
    print(f"✓ MD5值: {md5_value}")
    
    # 2. 构造请求数据
    print("\n📝 步骤2: 构造请求数据...")
    request_data = {
        "student_info": STUDENT_INFO,
        "assignment_id": ASSIGNMENT_ID,
        "metrics": METRICS,
        "checksums": {
            "evaluate.py": md5_value
        }
    }
    
    print("✓ 请求数据:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    # 3. 发送请求
    print(f"\n📝 步骤3: 发送POST请求到 {API_URL}...")
    response = send_request(API_URL, request_data)
    
    if response is None:
        return
    
    # 4. 显示响应
    print("\n📝 步骤4: 响应结果")
    print_response(response)
    
    # 5. 结果解析
    if response.status_code == 200:
        data = response.json()
        print("\n✅ 提交成功!")
        print(f"   消息: {data.get('message')}")
        print(f"   当前排名: {data.get('current_rank')}")
        print(f"   当前分数: {data.get('score')}")
        print(f"   提交次数: {data.get('submission_count')}")
        print(f"   排行榜更新: {data.get('leaderboard_updated')}")
    else:
        print(f"\n❌ 提交失败 (状态码: {response.status_code})")
        try:
            error_detail = response.json().get('detail', '未知错误')
            print(f"   错误信息: {error_detail}")
        except:
            pass


if __name__ == "__main__":
    main()

