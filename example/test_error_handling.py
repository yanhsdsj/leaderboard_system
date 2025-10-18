"""
测试三种错误处理机制的示例脚本
"""
import requests
import json
import hmac
import hashlib

BASE_URL = "http://localhost:8000"


def generate_client_signature(student_id, assignment_id, metrics):
    """生成客户端签名"""
    msg = (
        f"{student_id}:"
        f"{assignment_id}:"
        f"{metrics['MAE']}:"
        f"{metrics['MSE']}:"
        f"{metrics['RMSE']}:"
        f"{metrics['Prediction_Time']}"
    )
    secret = "ZeroGen-Leaderboard-Secret"
    return hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()


def test_timeout_error():
    """测试1：提交超时错误"""
    print("\n=== 测试1：提交超时错误 ===")
    
    # 使用一个已过期的作业ID（需要在assignments.json中配置过期时间）
    data = {
        "student_info": {
            "student_id": "test001",
            "name": "测试学生"
        },
        "assignment_id": "03",  # 作业03已过期
        "submission_data": {
            "metrics": {
                "MAE": 0.5,
                "MSE": 0.3,
                "RMSE": 0.55,
                "Prediction_Time": 0.02
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/submit", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


def test_signature_error():
    """测试2：签名不规范错误"""
    print("\n=== 测试2：签名不规范错误 ===")
    
    data = {
        "student_info": {
            "student_id": "test002",
            "name": "测试学生"
        },
        "assignment_id": "01",
        "submission_data": {
            "metrics": {
                "MAE": 4.2313,
                "MSE": 7.35235,
                "RMSE": 88.45345,
                "Prediction_Time": 4.2352
            }
        },
        "signature": "invalid_signature_12345"  # 错误的签名
    }
    
    response = requests.post(f"{BASE_URL}/api/submit", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


def test_correct_signature():
    """测试：正确的签名提交"""
    print("\n=== 测试：正确的签名提交 ===")
    
    metrics = {
        "MAE": 0.123,
        "MSE": 0.132,
        "RMSE": 0.324,
        "Prediction_Time": 0.34534
    }
    
    student_id = "test003"
    assignment_id = "01"
    
    # 生成正确的签名
    signature = generate_client_signature(student_id, assignment_id, metrics)
    
    data = {
        "student_info": {
            "student_id": student_id,
            "name": "测试学生"
        },
        "assignment_id": assignment_id,
        "submission_data": {
            "metrics": metrics
        },
        "signature": signature
    }
    
    response = requests.post(f"{BASE_URL}/api/submit", json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


def test_other_error():
    """测试3：其他错误（模拟）"""
    print("\n=== 测试3：其他错误 ===")
    print("注意：其他错误是捕获所有未预期的异常，无法直接模拟")
    print("但系统会捕获所有未处理的异常并返回统一格式：")
    print(json.dumps({
        "success": False,
        "message": "其他错误",
        "detail": "具体错误信息"
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    print("错误处理测试脚本")
    print("=" * 50)
    test_timeout_error()
    # 测试签名错误（这个可以正常测试）
    test_signature_error()
    
    # 测试正确的签名
    test_correct_signature()
    
    # 测试超时错误（需要配置过期的作业）
    print("\n注意：要测试提交超时错误，需要在 database/assignments.json 中")
    print("配置一个过期的作业，或修改现有作业的截止时间为过去的时间")
    
    # 其他错误说明
    test_other_error()
    
    print("\n" + "=" * 50)
    print("测试完成")

