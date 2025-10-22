"""
测试nickname更新功能
测试5次提交，RMSE分别为：0.5, 0.2, 0.5, 0.3, 0.1
在第2、3、5次提交时修改nickname
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# 测试学生信息（从list.json中选择）
STUDENT = {
    "student_id": "10212140414",
    "name": "盛子骜"
}

# 5次提交的数据
SUBMISSIONS = [
    {
        "round": 1,
        "nickname": "昵称1号",
        "rmse": 0.5,
        "mae": 0.450,
        "mse": 0.250,
        "prediction_time": 2.0,
        "nickname_changed": False
    },
    {
        "round": 2,
        "nickname": "昵称2号_修改",
        "rmse": 0.2,
        "mae": 0.180,
        "mse": 0.040,
        "prediction_time": 1.5,
        "nickname_changed": True  # 修改nickname
    },
    {
        "round": 3,
        "nickname": "昵称3号_再次修改",
        "rmse": 0.5,
        "mae": 0.450,
        "mse": 0.250,
        "prediction_time": 2.2,
        "nickname_changed": True  # 修改nickname
    },
    {
        "round": 4,
        "nickname": "昵称3号_再次修改",  # 保持不变
        "rmse": 0.3,
        "mae": 0.270,
        "mse": 0.090,
        "prediction_time": 1.8,
        "nickname_changed": False
    },
    {
        "round": 5,
        "nickname": "最终昵称_第5次修改",
        "rmse": 0.1,
        "mae": 0.090,
        "mse": 0.010,
        "prediction_time": 1.2,
        "nickname_changed": True  # 修改nickname
    }
]


def wait_for_space():
    """
    等待用户按空格键继续
    """
    while True:
        user_input = input()
        if user_input == '' or ' ' in user_input or user_input.strip() == '':
            break
        else:
            print("请按空格键（或直接按回车）继续...")


def submit_assignment(student_id, name, nickname, mae, mse, rmse, prediction_time, assignment_id="01"):
    """
    提交作业
    """
    data = {
        "student_info": {
            "student_id": student_id,
            "name": name,
            "nickname": nickname
        },
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
            return True, result
        else:
            error = response.json()
            return False, error.get('detail', '未知错误')
    except Exception as e:
        return False, str(e)


def print_header():
    """
    打印测试头部
    """
    print("\n" + "="*80)
    print("测试 Nickname 更新功能")
    print("="*80)
    print(f"测试学生: {STUDENT['name']} ({STUDENT['student_id']})")
    print(f"作业ID: 01")
    print(f"总提交次数: {len(SUBMISSIONS)}次")
    print("="*80)


def print_submission_info(submission_data, is_before=True):
    """
    打印提交信息
    """
    if is_before:
        print(f"\n📋 第{submission_data['round']}次提交准备")
        print("-" * 60)
        print(f"  Nickname: {submission_data['nickname']}", end="")
        if submission_data['nickname_changed']:
            print(" 🔄 [将修改nickname]")
        else:
            print()
        print(f"  RMSE: {submission_data['rmse']}")
        print(f"  MAE: {submission_data['mae']}")
        print(f"  MSE: {submission_data['mse']}")
        print(f"  推理时间: {submission_data['prediction_time']}s")
    else:
        print("-" * 60)


def print_result(success, result, submission_data):
    """
    打印提交结果
    """
    if success:
        print(f"\n✅ 提交成功!")
        print(f"  消息: {result['message']}")
        print(f"  提交次数: {result['submission_count']}")
        print(f"  当前分数: {result['score']:.6f}")
        if result['previous_score'] is not None:
            print(f"  之前分数: {result['previous_score']:.6f}")
        if result['current_rank']:
            print(f"  当前排名: 第{result['current_rank']}名")
        print(f"  排行榜更新: {'是' if result['leaderboard_updated'] else '否'}")
        
        # 特别标注nickname是否被修改
        if submission_data['nickname_changed']:
            print(f"\n  🔄 Nickname已更新为: {submission_data['nickname']}")
    else:
        print(f"\n❌ 提交失败: {result}")


def print_summary():
    """
    打印测试总结
    """
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    print(f"总提交次数: {len(SUBMISSIONS)}次")
    print(f"\nNickname变化轨迹:")
    for i, sub in enumerate(SUBMISSIONS, 1):
        marker = " 🔄 [修改]" if sub['nickname_changed'] else ""
        print(f"  第{i}次: {sub['nickname']}{marker}")
    
    print(f"\n成绩变化:")
    best_rmse = min(sub['rmse'] for sub in SUBMISSIONS)
    for i, sub in enumerate(SUBMISSIONS, 1):
        marker = " ⭐ [最佳]" if sub['rmse'] == best_rmse else ""
        print(f"  第{i}次: RMSE={sub['rmse']}{marker}")
    
    print(f"\n预期结果:")
    print(f"  - 排行榜显示的nickname: {SUBMISSIONS[-1]['nickname']}")
    print(f"  - 排行榜显示的RMSE: {best_rmse}")
    print(f"  - 提交次数: {len(SUBMISSIONS)}")
    
    print("\n验证步骤:")
    print("  1. 访问前端页面")
    print("  2. 查看作业一排行榜")
    print(f"  3. 确认学号 {STUDENT['student_id']} 的nickname是: {SUBMISSIONS[-1]['nickname']}")
    print(f"  4. 确认RMSE是: {best_rmse}")
    print("  5. 点击学号查看提交详情")
    print("  6. 确认有5次提交记录，且第5次是最佳提交（RMSE最小）")
    print("="*80)


def main():
    """
    主函数
    """
    print_header()
    
    print("\n💡 说明:")
    print("  - 每次提交前会显示详细信息")
    print("  - 按空格键（或回车）继续下一次提交")
    print("  - 🔄 标记表示该次提交会修改nickname")
    print("  - 最佳成绩是第5次提交（RMSE=0.1，最小最好）")
    print("  - Nickname会在第2、3、5次提交时修改")
    
    input("\n按空格键（或回车）开始测试...")
    
    # 执行5次提交
    for submission_data in SUBMISSIONS:
        print_submission_info(submission_data, is_before=True)
        
        print(f"\n⏸️  按空格键（或回车）提交第{submission_data['round']}次作业...")
        wait_for_space()
        
        # 提交
        success, result = submit_assignment(
            STUDENT['student_id'],
            STUDENT['name'],
            submission_data['nickname'],
            submission_data['mae'],
            submission_data['mse'],
            submission_data['rmse'],
            submission_data['prediction_time']
        )
        
        # 显示结果
        print_result(success, result, submission_data)
        
        if not success:
            print("\n⚠️  提交失败，测试终止")
            return
        
        print_submission_info(submission_data, is_before=False)
    
    # 打印总结
    print_summary()
    
    print("\n🎉 测试完成！请访问前端页面验证结果。")


if __name__ == "__main__":
    main()

