"""
测试提交验证功能
测试场景：
1. 无效的 assignment_id
2. 缺少必需的指标字段
3. 指标值为负数
4. 正常提交
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_invalid_assignment_id():
    """测试无效的作业ID"""
    print("\n=== 测试1: 无效的作业ID ===")
    
    data = {
        "student_info": {
            "student_id": "10225101460",
            "name": "测试学生",
            "nickname": "Tester"
        },
        "assignment_id": "99",  # 不存在的作业ID
        "metrics": {
            "MAE": 0.5,
            "MSE": 0.3,
            "RMSE": 0.4,
            "Prediction_Time": 1.2
        },
        "checksums": {
            "evaluate.py": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")


def test_missing_metrics():
    """测试缺少必需的指标字段"""
    print("\n=== 测试2: 缺少必需的指标字段 ===")
    
    data = {
        "student_info": {
            "student_id": "10225101460",
            "name": "测试学生",
            "nickname": "Tester"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": 0.5,
            "MSE": 0.3
            # 缺少 RMSE 和 Prediction_Time
        },
        "checksums": {
            "evaluate.py": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")


def test_negative_metrics():
    """测试指标值为负数"""
    print("\n=== 测试3: 指标值为负数 ===")
    
    data = {
        "student_info": {
            "student_id": "10225101460",
            "name": "测试学生",
            "nickname": "Tester"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": -0.5,  # 负数
            "MSE": 0.3,
            "RMSE": 0.4,
            "Prediction_Time": 1.2
        },
        "checksums": {
            "evaluate.py": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")


def test_valid_submission():
    """测试正常提交"""
    print("\n=== 测试4: 正常提交 ===")
    
    data = {
        "student_info": {
            "student_id": "10225101460",
            "name": "测试学生",
            "nickname": "Tester"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": 0.5,
            "MSE": 0.3,
            "RMSE": 0.4,
            "Prediction_Time": 1.2
        },
        "checksums": {
            "evaluate.py": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")


def test_missing_all_metrics():
    """测试缺少所有指标字段"""
    print("\n=== 测试5: 缺少所有指标字段 ===")
    
    data = {
        "student_info": {
            "student_id": "10225101460",
            "name": "测试学生",
            "nickname": "Tester"
        },
        "assignment_id": "01",
        "metrics": {},  # 空字典
        "checksums": {
            "evaluate.py": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("提交验证测试")
    print("=" * 60)
    
    # 运行所有测试
    test_invalid_assignment_id()
    test_missing_metrics()
    test_negative_metrics()
    test_valid_submission()
    test_missing_all_metrics()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

