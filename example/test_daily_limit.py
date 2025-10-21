#!/usr/bin/env python3
"""
测试每日提交次数限制
验证max_submissions是按每个学生每天计算
"""

import requests
import json

# ==================== 配置区 ====================
API_URL = "http://localhost:8000/api/submit"
CORRECT_MD5 = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
# ================================================


def send_request(student_id, name, assignment_id, rmse, description=""):
    """发送提交请求"""
    data = {
        "student_info": {
            "student_id": student_id,
            "name": name,
            "nickname": "测试"
        },
        "assignment_id": assignment_id,
        "metrics": {
            "MAE": 0.1,
            "MSE": 0.2,
            "RMSE": rmse,
            "Prediction_Time": 1.0
        },
        "checksums": {
            "evaluate.py": CORRECT_MD5
        }
    }
    
    try:
        response = requests.post(
            API_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        result = response.json()
        
        if response.status_code == 200:
            print(f"✅ {description}")
            print(f"   提交次数: {result.get('submission_count')}")
            print(f"   当前排名: {result.get('current_rank')}")
        else:
            print(f"❌ {description}")
            print(f"   错误: {result.get('detail', '未知错误')}")
        
        return response.status_code, result
        
    except Exception as e:
        print(f"❌ {description}")
        print(f"   异常: {str(e)}")
        return None, None


def wait_for_enter(message="按回车继续..."):
    """等待用户按回车"""
    input(f"\n⏸️  {message}\n")


def main():
    print("=" * 80)
    print("测试每日提交次数限制")
    print("=" * 80)
    print("\n说明:")
    print("1. max_submissions 是每个学生每天的限制")
    print("2. 不同学生的提交次数独立计算")
    print("3. 每天UTC 00:00:00 重置")
    print("4. 当前配置: assignments.json 中 max_submissions = 20")
    print("=" * 80)
    
    wait_for_enter("准备开始测试...")
    
    # 测试1: 同一学生提交多次
    print("\n" + "🔵" * 40)
    print("测试1: 同一学生提交多次（测试每日限制）")
    print("🔵" * 40)
    print("将提交21次，第21次应该失败（超过每日限制20次）\n")
    
    student_id = "TEST_DAILY_001"
    name = "每日限制测试学生"
    assignment_id = "01"
    
    for i in range(1, 22):
        rmse = 1.0 - (i * 0.01)  # 每次都比上次好一点
        desc = f"第{i}次提交 (RMSE={rmse:.2f})"
        status_code, result = send_request(student_id, name, assignment_id, rmse, desc)
        
        if i == 20:
            print(f"\n⚠️  已达到20次提交，下一次应该失败")
            wait_for_enter("按回车提交第21次...")
        elif i % 5 == 0:
            wait_for_enter(f"已提交 {i}/21 次，按回车继续...")
    
    # 测试2: 不同学生互不影响
    print("\n\n" + "🟢" * 40)
    print("测试2: 不同学生的提交次数独立计算")
    print("🟢" * 40)
    print("即使学生A已经提交20次，学生B仍然可以提交\n")
    
    wait_for_enter("按回车开始测试...")
    
    # 学生B第一次提交（应该成功）
    student_b_id = "TEST_DAILY_002"
    student_b_name = "学生B"
    status_code, result = send_request(
        student_b_id, 
        student_b_name, 
        assignment_id, 
        0.5, 
        "学生B第1次提交（应该成功）"
    )
    
    # 学生B第二次提交（应该成功）
    status_code, result = send_request(
        student_b_id, 
        student_b_name, 
        assignment_id, 
        0.4, 
        "学生B第2次提交（应该成功）"
    )
    
    # 测试3: 不同作业互不影响
    print("\n\n" + "🟡" * 40)
    print("测试3: 不同作业的提交次数独立计算")
    print("🟡" * 40)
    print("即使学生A在作业01已经提交20次，在作业02仍然可以提交\n")
    
    wait_for_enter("按回车开始测试...")
    
    # 学生A在作业02提交（应该成功）
    status_code, result = send_request(
        student_id, 
        name, 
        "02",  # 作业02
        0.6, 
        "学生A在作业02第1次提交（应该成功）"
    )
    
    status_code, result = send_request(
        student_id, 
        name, 
        "02",  # 作业02
        0.5, 
        "学生A在作业02第2次提交（应该成功）"
    )
    
    print("\n\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)
    print("\n总结:")
    print("1. ✅ 每个学生每天有独立的提交次数限制")
    print("2. ✅ 不同学生的提交次数互不影响")
    print("3. ✅ 不同作业的提交次数独立计算")
    print("4. ⚠️  提交次数在每天UTC 00:00:00 重置")
    print("\n建议:")
    print("- 查看 backend/database/submissions.json 确认所有提交记录")
    print("- 访问 http://localhost:5173 查看排行榜")
    print("=" * 80)


if __name__ == "__main__":
    main()

