#!/usr/bin/env python3
"""
综合测试脚本
测试排行榜系统的各种场景
"""

import requests
import json
import hashlib
from datetime import datetime

# ==================== 配置区 ====================
API_URL = "http://localhost:8000/api/submit"
CORRECT_MD5 = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
# ================================================


def send_request(data, description=""):
    """发送POST请求并打印结果"""
    print("\n" + "=" * 80)
    if description:
        print(f"📝 {description}")
    print("=" * 80)
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            API_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n状态码: {response.status_code}")
        try:
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200:
                print(f"\n✅ 成功: {result.get('message')}")
                print(f"   提交次数: {result.get('submission_count')}")
                print(f"   当前排名: {result.get('current_rank')}")
                print(f"   当前分数: {result.get('score')}")
                print(f"   排行榜更新: {result.get('leaderboard_updated')}")
            else:
                print(f"\n❌ 失败: {result.get('detail', '未知错误')}")
        except:
            print(f"响应: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 错误: 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
    
    print("=" * 80)


def wait_for_enter(message="按回车继续..."):
    """等待用户按回车"""
    input(f"\n⏸️  {message}\n")


def test_1_correct_submission():
    """测试1: 学生正确提交"""
    print("\n\n" + "🔵" * 40)
    print("测试1: 学生正确提交")
    print("🔵" * 40)
    
    data = {
        "student_info": {
            "student_id": "2024001",
            "name": "测试学生A",
            "nickname": "正确提交者"
        },
        "assignment_id": "01",
            "metrics": {
            "MAE": 0.1234,
            "MSE": 0.5678,
            "RMSE": 0.7536,
            "Prediction_Time": 12.34
        },
        "checksums": {
            "evaluate.py": CORRECT_MD5
        }
    }
    
    send_request(data, "正确提交示例")


def test_2_validation_errors():
    """测试2: 验证错误的多种问题"""
    print("\n\n" + "🔴" * 40)
    print("测试2: 验证错误场景")
    print("🔴" * 40)
    
    # 2.1 MD5校验失败
    data = {
        "student_info": {
            "student_id": "2024002",
            "name": "测试学生B",
            "nickname": "错误MD5"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": 0.1,
            "MSE": 0.2,
            "RMSE": 0.3,
            "Prediction_Time": 1.0
        },
        "checksums": {
            "evaluate.py": "wrong_md5_checksum_12345678"
        }
    }
    send_request(data, "错误场景1: MD5校验失败")
    wait_for_enter()
    
    # 2.2 截止时间超时
    data = {
        "student_info": {
            "student_id": "2024003",
            "name": "测试学生C",
            "nickname": "超时提交"
        },
        "assignment_id": "03",  # 作业3已超时
        "metrics": {
            "MAE": 0.1,
            "MSE": 0.2,
            "RMSE": 0.3,
            "Prediction_Time": 1.0
        },
        "checksums": {
            "evaluate.py": CORRECT_MD5
        }
    }
    send_request(data, "错误场景2: 截止时间超时")
    wait_for_enter()
    
    # 2.3 缺少student_id字段
    data = {
        "student_info": {
            "name": "测试学生D",
            "nickname": "缺少学号"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": 0.1,
            "MSE": 0.2,
            "RMSE": 0.3,
            "Prediction_Time": 1.0
        },
        "checksums": {
            "evaluate.py": CORRECT_MD5
        }
    }
    send_request(data, "错误场景3: 缺少必填字段student_id")
    wait_for_enter()
    
    # 2.4 缺少name字段
    data = {
        "student_info": {
            "student_id": "2024004",
            "nickname": "缺少姓名"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": 0.1,
            "MSE": 0.2,
            "RMSE": 0.3,
            "Prediction_Time": 1.0
        },
        "checksums": {
            "evaluate.py": CORRECT_MD5
        }
    }
    send_request(data, "错误场景4: 缺少必填字段name")
    wait_for_enter()
    
    # 2.5 metrics字段类型错误
    data = {
        "student_info": {
            "student_id": "2024005",
            "name": "测试学生E",
            "nickname": "类型错误"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": "not_a_number",
            "MSE": 0.2,
            "RMSE": 0.3,
            "Prediction_Time": 1.0
        },
        "checksums": {
            "evaluate.py": CORRECT_MD5
        }
    }
    send_request(data, "错误场景5: metrics字段类型错误")
    wait_for_enter()
    
    # 2.6 缺少metrics字段
    data = {
        "student_info": {
            "student_id": "2024006",
            "name": "测试学生F",
            "nickname": "缺少指标"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": 0.1,
            "MSE": 0.2,
            "RMSE": 0.3
            # 缺少Prediction_Time
        },
        "checksums": {
            "evaluate.py": CORRECT_MD5
        }
    }
    send_request(data, "错误场景6: 缺少metrics必填字段Prediction_Time")
    wait_for_enter()
    
    # 2.7 不存在的作业ID
    data = {
        "student_info": {
            "student_id": "2024007",
            "name": "测试学生G",
            "nickname": "错误作业"
        },
        "assignment_id": "99",  # 不存在的作业
        "metrics": {
            "MAE": 0.1,
            "MSE": 0.2,
            "RMSE": 0.3,
            "Prediction_Time": 1.0
        },
        "checksums": {
            "evaluate.py": CORRECT_MD5
        }
    }
    send_request(data, "错误场景7: 不存在的作业ID")
    wait_for_enter()
    
    # 2.8 缺少checksums字段
    data = {
        "student_info": {
            "student_id": "2024008",
            "name": "测试学生H",
            "nickname": "缺少校验"
        },
        "assignment_id": "01",
        "metrics": {
            "MAE": 0.1,
            "MSE": 0.2,
            "RMSE": 0.3,
            "Prediction_Time": 1.0
        },
        "checksums": {}
    }
    send_request(data, "错误场景8: 缺少checksums.evaluate.py")
    wait_for_enter()


def test_3_same_student_multiple_submissions():
    """测试3: 同一学生多次提交同一作业，检查排序逻辑"""
    print("\n\n" + "🟢" * 40)
    print("测试3: 同一学生多次提交同一作业（10个提交）")
    print("🟢" * 40)
    
    student_id = "2024100"
    assignment_id = "01"
    
    # 10个提交，RMSE有升有降
    submissions = [
        {"RMSE": 1.500, "Prediction_Time": 10.0, "desc": "第1次: RMSE=1.500"},
        {"RMSE": 1.200, "Prediction_Time": 12.0, "desc": "第2次: RMSE=1.200 (提升)"},
        {"RMSE": 1.300, "Prediction_Time": 8.0, "desc": "第3次: RMSE=1.300 (未提升)"},
        {"RMSE": 1.000, "Prediction_Time": 15.0, "desc": "第4次: RMSE=1.000 (提升)"},
        {"RMSE": 1.100, "Prediction_Time": 9.0, "desc": "第5次: RMSE=1.100 (未提升)"},
        {"RMSE": 0.800, "Prediction_Time": 20.0, "desc": "第6次: RMSE=0.800 (提升)"},
        {"RMSE": 0.900, "Prediction_Time": 7.0, "desc": "第7次: RMSE=0.900 (未提升)"},
        {"RMSE": 0.800, "Prediction_Time": 18.0, "desc": "第8次: RMSE=0.800 (相同RMSE，但时间未提升)"},
        {"RMSE": 0.800, "Prediction_Time": 16.0, "desc": "第9次: RMSE=0.800 (相同RMSE，时间提升)"},
        {"RMSE": 0.600, "Prediction_Time": 25.0, "desc": "第10次: RMSE=0.600 (提升)"},
    ]
    
    for i, sub in enumerate(submissions, 1):
        data = {
            "student_info": {
                "student_id": student_id,
                "name": "多次提交测试学生",
                "nickname": "排序测试"
            },
            "assignment_id": assignment_id,
            "metrics": {
                "MAE": 0.1 * i,
                "MSE": 0.2 * i,
                "RMSE": sub["RMSE"],
                "Prediction_Time": sub["Prediction_Time"]
            },
            "checksums": {
                "evaluate.py": CORRECT_MD5
            }
        }
        
        send_request(data, sub["desc"])
        
        if i % 2 == 0:  # 每2个暂停
            wait_for_enter(f"已提交 {i}/10，按回车继续...")


def test_4_multiple_students_different_assignments():
    """测试4: 多个学生提交不同作业，检查排序逻辑"""
    print("\n\n" + "🟡" * 40)
    print("测试4: 多个学生提交不同作业（15个提交）")
    print("🟡" * 40)
    
    submissions = [
        # 作业01的提交
        {"student_id": "2024201", "name": "学生A", "assignment": "01", "RMSE": 0.850, "time": 10.5},
        {"student_id": "2024202", "name": "学生B", "assignment": "01", "RMSE": 0.720, "time": 12.3},
        {"student_id": "2024203", "name": "学生C", "assignment": "01", "RMSE": 0.900, "time": 8.7},
        {"student_id": "2024204", "name": "学生D", "assignment": "01", "RMSE": 0.720, "time": 9.5},  # 与学生B相同RMSE
        {"student_id": "2024205", "name": "学生E", "assignment": "01", "RMSE": 0.650, "time": 15.2},
        
        # 作业02的提交
        {"student_id": "2024206", "name": "学生F", "assignment": "02", "RMSE": 1.100, "time": 20.0},
        {"student_id": "2024207", "name": "学生G", "assignment": "02", "RMSE": 0.950, "time": 18.5},
        {"student_id": "2024208", "name": "学生H", "assignment": "02", "RMSE": 1.200, "time": 16.0},
        {"student_id": "2024209", "name": "学生I", "assignment": "02", "RMSE": 0.800, "time": 22.5},
        {"student_id": "2024210", "name": "学生J", "assignment": "02", "RMSE": 0.950, "time": 17.0},  # 与学生G相同RMSE
        
        # 混合提交
        {"student_id": "2024211", "name": "学生K", "assignment": "01", "RMSE": 0.720, "time": 10.0},  # 与前面相同RMSE
        {"student_id": "2024212", "name": "学生L", "assignment": "02", "RMSE": 0.700, "time": 25.0},
        {"student_id": "2024213", "name": "学生M", "assignment": "01", "RMSE": 0.600, "time": 20.0},
        {"student_id": "2024214", "name": "学生N", "assignment": "02", "RMSE": 0.650, "time": 30.0},
        {"student_id": "2024215", "name": "学生O", "assignment": "01", "RMSE": 0.550, "time": 25.5},
    ]
    
    for i, sub in enumerate(submissions, 1):
        data = {
            "student_info": {
                "student_id": sub["student_id"],
                "name": sub["name"],
                "nickname": f"测试{i}"
            },
            "assignment_id": sub["assignment"],
            "metrics": {
                "MAE": 0.1,
                "MSE": 0.2,
                "RMSE": sub["RMSE"],
                "Prediction_Time": sub["time"]
            },
            "checksums": {
                "evaluate.py": CORRECT_MD5
            }
        }
        
        send_request(data, f"学生{sub['name']}提交作业{sub['assignment']} (RMSE={sub['RMSE']}, Time={sub['time']})")
        
        if i % 3 == 0:  # 每3个暂停
            wait_for_enter(f"已提交 {i}/15，按回车继续...")


def main():
    print("=" * 80)
    print("排行榜系统 - 综合测试脚本")
    print("=" * 80)
    print("\n测试内容:")
    print("1. 学生正确提交")
    print("2. 验证错误场景（8种错误情况）")
    print("3. 同一学生多次提交同一作业（10个提交，测试排序逻辑）")
    print("4. 多个学生提交不同作业（15个提交，测试排序逻辑）")
    print("\n" + "=" * 80)
    
    wait_for_enter("准备开始测试，按回车继续...")
    
    # 测试1: 正确提交
    test_1_correct_submission()
    wait_for_enter("测试1完成，按回车继续测试2...")
    
    # 测试2: 验证错误
    test_2_validation_errors()
    wait_for_enter("测试2完成，按回车继续测试3...")
    
    # 测试3: 同一学生多次提交
    test_3_same_student_multiple_submissions()
    wait_for_enter("测试3完成，按回车继续测试4...")
    
    # 测试4: 多个学生不同作业
    test_4_multiple_students_different_assignments()
    
    print("\n\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)
    print("\n建议:")
    print("1. 访问 http://localhost:5173 查看排行榜前端")
    print("2. 检查作业01和作业02的排行榜排序是否正确")
    print("3. 检查学生2024100的多次提交历史")
    print("=" * 80)


if __name__ == "__main__":
    main()
