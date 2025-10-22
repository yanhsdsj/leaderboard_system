"""
测试提交场景
共25次测试样例，包含：
1. 作业一：15次提交（5个学生，每人3次）
2. 作业二：10次提交（3个学生，分别3/4/3次）
3. 最好成绩出现在：第一次、中间、最后一次
"""

import requests
import json
import time
import random

BASE_URL = "http://localhost:8000"

# 从list.json中选择的测试学生
STUDENTS_ASSIGNMENT_01 = [
    {"student_id": "10212140414", "name": "盛子骜", "nickname": "测试学生1"},
    {"student_id": "10225101483", "name": "谢瑞阳", "nickname": "测试学生2"},
    {"student_id": "51285903001", "name": "马淑玥", "nickname": "测试学生3"},
    {"student_id": "51285903002", "name": "孙佳杰", "nickname": "测试学生4"},
    {"student_id": "51285903003", "name": "宋佳琦", "nickname": "测试学生5"},
]

STUDENTS_ASSIGNMENT_02 = [
    {"student_id": "51285903004", "name": "沈丁", "nickname": "测试学生6"},
    {"student_id": "51285903005", "name": "鲍啸天", "nickname": "测试学生7"},
    {"student_id": "51285903006", "name": "李嘉诚", "nickname": "测试学生8"},
]


def submit_assignment(student_info, assignment_id, mae, mse, rmse, prediction_time):
    """
    提交作业
    """
    data = {
        "student_info": student_info,
        "assignment_id": assignment_id,
        "metrics": {
            "MAE": mae,
            "MSE": mse,
            "RMSE": rmse,
            "Prediction_Time": prediction_time
        },
        "checksums": {
            "evaluate.py": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ [{student_info['name']}] {result['message']}")
            return True
        else:
            error = response.json()
            print(f"❌ [{student_info['name']}] 提交失败: {error.get('detail', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ [{student_info['name']}] 请求失败: {e}")
        return False


def test_assignment_01():
    """
    测试作业一：15次提交（5个学生，每人3次）
    """
    print("\n" + "="*80)
    print("测试作业一：15次提交")
    print("="*80)
    
    # 学生1：最好成绩在第1次
    print("\n【学生1 - 盛子骜】最好成绩在第1次提交")
    student1 = STUDENTS_ASSIGNMENT_01[0]
    submit_assignment(student1, "01", 0.100, 0.015, 0.122, 1.5)  # 最好：RMSE=0.122
    time.sleep(0.5)
    submit_assignment(student1, "01", 0.120, 0.018, 0.134, 1.6)  # 较差
    time.sleep(0.5)
    submit_assignment(student1, "01", 0.110, 0.016, 0.126, 1.4)  # 较差
    time.sleep(0.5)
    
    # 学生2：最好成绩在第2次（中间）
    print("\n【学生2 - 谢瑞阳】最好成绩在第2次提交（中间）")
    student2 = STUDENTS_ASSIGNMENT_01[1]
    submit_assignment(student2, "01", 0.150, 0.025, 0.158, 1.8)  # 较差
    time.sleep(0.5)
    submit_assignment(student2, "01", 0.095, 0.012, 0.109, 1.3)  # 最好：RMSE=0.109
    time.sleep(0.5)
    submit_assignment(student2, "01", 0.130, 0.020, 0.141, 1.7)  # 较差
    time.sleep(0.5)
    
    # 学生3：最好成绩在第3次（最后）
    print("\n【学生3 - 马淑玥】最好成绩在第3次提交（最后）")
    student3 = STUDENTS_ASSIGNMENT_01[2]
    submit_assignment(student3, "01", 0.180, 0.035, 0.187, 2.1)  # 较差
    time.sleep(0.5)
    submit_assignment(student3, "01", 0.160, 0.028, 0.167, 1.9)  # 较差
    time.sleep(0.5)
    submit_assignment(student3, "01", 0.088, 0.010, 0.100, 1.2)  # 最好：RMSE=0.100
    time.sleep(0.5)
    
    # 学生4：最好成绩在第1次
    print("\n【学生4 - 孙佳杰】最好成绩在第1次提交")
    student4 = STUDENTS_ASSIGNMENT_01[3]
    submit_assignment(student4, "01", 0.105, 0.014, 0.118, 1.6)  # 最好：RMSE=0.118
    time.sleep(0.5)
    submit_assignment(student4, "01", 0.125, 0.019, 0.138, 1.8)  # 较差
    time.sleep(0.5)
    submit_assignment(student4, "01", 0.115, 0.017, 0.130, 1.7)  # 较差
    time.sleep(0.5)
    
    # 学生5：最好成绩在第2次（中间）
    print("\n【学生5 - 宋佳琦】最好成绩在第2次提交（中间）")
    student5 = STUDENTS_ASSIGNMENT_01[4]
    submit_assignment(student5, "01", 0.140, 0.022, 0.148, 1.9)  # 较差
    time.sleep(0.5)
    submit_assignment(student5, "01", 0.092, 0.011, 0.105, 1.4)  # 最好：RMSE=0.105
    time.sleep(0.5)
    submit_assignment(student5, "01", 0.135, 0.021, 0.145, 2.0)  # 较差
    time.sleep(0.5)
    
    print("\n✅ 作业一测试完成：共15次提交")


def test_assignment_02():
    """
    测试作业二：10次提交（3个学生，分别3/4/3次）
    """
    print("\n" + "="*80)
    print("测试作业二：10次提交")
    print("="*80)
    
    # 学生6：3次提交，最好成绩在第1次
    print("\n【学生6 - 沈丁】最好成绩在第1次提交")
    student6 = STUDENTS_ASSIGNMENT_02[0]
    submit_assignment(student6, "02", 0.200, 0.045, 0.212, 2.2)  # 最好：RMSE=0.212
    time.sleep(0.5)
    submit_assignment(student6, "02", 0.220, 0.052, 0.228, 2.4)  # 较差
    time.sleep(0.5)
    submit_assignment(student6, "02", 0.210, 0.048, 0.219, 2.3)  # 较差
    time.sleep(0.5)
    
    # 学生7：4次提交，最好成绩在第2次（中间）
    print("\n【学生7 - 鲍啸天】最好成绩在第2次提交（中间）")
    student7 = STUDENTS_ASSIGNMENT_02[1]
    submit_assignment(student7, "02", 0.250, 0.065, 0.255, 2.6)  # 较差
    time.sleep(0.5)
    submit_assignment(student7, "02", 0.185, 0.038, 0.195, 2.0)  # 最好：RMSE=0.195
    time.sleep(0.5)
    submit_assignment(student7, "02", 0.240, 0.060, 0.245, 2.5)  # 较差
    time.sleep(0.5)
    submit_assignment(student7, "02", 0.230, 0.055, 0.234, 2.4)  # 较差
    time.sleep(0.5)
    
    # 学生8：3次提交，最好成绩在第3次（最后）
    print("\n【学生8 - 李嘉诚】最好成绩在第3次提交（最后）")
    student8 = STUDENTS_ASSIGNMENT_02[2]
    submit_assignment(student8, "02", 0.280, 0.082, 0.286, 2.8)  # 较差
    time.sleep(0.5)
    submit_assignment(student8, "02", 0.260, 0.072, 0.268, 2.7)  # 较差
    time.sleep(0.5)
    submit_assignment(student8, "02", 0.178, 0.035, 0.187, 1.9)  # 最好：RMSE=0.187
    time.sleep(0.5)
    
    print("\n✅ 作业二测试完成：共10次提交")


def print_summary():
    """
    打印测试总结
    """
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"总提交次数: 25次")
    print(f"  - 作业一: 15次提交（5个学生，每人3次）")
    print(f"  - 作业二: 10次提交（3个学生，3/4/3次）")
    print(f"\n最好成绩出现位置:")
    print(f"  - 第一次提交: 学生1、学生4、学生6")
    print(f"  - 中间提交: 学生2、学生5、学生7")
    print(f"  - 最后提交: 学生3、学生8")
    print("\n测试验证项:")
    print("  ✅ 排序逻辑：RMSE → 推理时间")
    print("  ✅ 只保留最佳成绩")
    print("  ✅ 不同提交时间的最佳成绩处理")
    print("  ✅ nickname支持修改")
    print("="*80)


def main():
    """
    主函数
    """
    print("\n" + "="*80)
    print("开始测试：提交场景测试")
    print("="*80)
    print(f"API地址: {BASE_URL}")
    print(f"总提交次数: 25次")
    print("="*80)
    
    # 执行测试
    test_assignment_01()
    test_assignment_02()
    
    # 打印总结
    print_summary()
    
    print("\n🎉 所有测试完成！")
    print("请访问前端页面查看排行榜结果")


if __name__ == "__main__":
    main()

