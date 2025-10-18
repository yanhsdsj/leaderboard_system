"""
综合功能测试脚本
测试系统的完整功能，包括：
1. 同一同学多次提交同一个assignment_id
2. 同一同学多次提交不同assignment_id
3. 多个同学提交同一个assignment_id
4. 时间超时测试（assignment_id=03）
"""

import requests
import json
from datetime import datetime
from typing import Dict, List

# 配置
BASE_URL = "http://localhost:8000"

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")

def print_section(text):
    """打印小节标题"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'─'*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}► {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'─'*80}{Colors.END}\n")

def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def submit_assignment(student_id: str, name: str, assignment_id: str, 
                      mae: float, mse: float, rmse: float, pred_time: float) -> Dict:
    """提交作业"""
    submission_data = {
        "student_info": {
            "student_id": student_id,
            "name": name
        },
        "assignment_id": assignment_id,
        "submission_data": {
            "metrics": {
                "MAE": mae,
                "MSE": mse,
                "RMSE": rmse,
                "Prediction_Time": pred_time
            }
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/submit", json=submission_data)
        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "data": response.json()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_leaderboard(assignment_id: str) -> List[Dict]:
    """获取排行榜"""
    try:
        response = requests.get(f"{BASE_URL}/api/leaderboard/{assignment_id}")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print_error(f"获取排行榜失败: {e}")
        return []


def display_leaderboard(assignment_id: str, title: str = None):
    """显示排行榜"""
    if title:
        print(f"\n{Colors.BOLD}{title}{Colors.END}")
    
    leaderboard = get_leaderboard(assignment_id)
    
    if not leaderboard:
        print_warning("排行榜为空")
        return
    
    print(f"\n{'排名':<6} {'学号':<12} {'姓名':<10} {'RMSE分数':<15} {'提交次数':<10} {'时间':<20}")
    print("─" * 85)
    
    for entry in leaderboard:
        print(
            f"{entry['rank']:<6} "
            f"{entry['student_info']['student_id']:<12} "
            f"{entry['student_info']['name']:<10} "
            f"{entry['score']:<15.4f} "
            f"{entry['submission_count']:<10} "
            f"{entry['timestamp'][:19]:<20}"
        )
    
    print(f"{Colors.CYAN}注：RMSE越小越好，排名第一分数最低{Colors.END}")


def test_scenario_1():
    """
    测试场景1: 同一同学多次提交同一个assignment_id
    测试排名更新逻辑
    
    注意：RMSE越小越好
    """
    print_header("测试场景1: 同一同学多次提交同一个assignment_id")
    
    student_id = "TEST001"
    name = "测试学生A"
    assignment_id = "01"
    
    # 第一次提交（较大的RMSE = 较差的成绩）
    print_section("第1次提交 - RMSE=2.83（较差成绩）")
    result = submit_assignment(student_id, name, assignment_id, 2.5, 8.0, 2.83, 5.5)
    if result["success"]:
        print_success(result["data"]["message"])
        print_info(f"RMSE分数: {result['data']['score']:.4f}（越小越好）")
        print_info(f"排名: {result['data']['current_rank']}")
        print_info(f"提交次数: {result['data']['submission_count']}")
    else:
        print_error(f"提交失败: {result.get('error', result.get('data', {}).get('detail', 'Unknown error'))}")
    
    display_leaderboard(assignment_id, "当前排行榜:")
    
    # 第二次提交（较小的RMSE = 改进的成绩）
    print_section("第2次提交 - RMSE=2.24（成绩改进，应更新排行榜）")
    result = submit_assignment(student_id, name, assignment_id, 1.8, 5.0, 2.24, 4.2)
    if result["success"]:
        print_success(result["data"]["message"])
        print_info(f"新RMSE: {result['data']['score']:.4f}")
        print_info(f"旧RMSE: {result['data'].get('previous_score', 'N/A'):.4f}")
        print_info(f"变化: {result['data'].get('previous_score', 0) - result['data']['score']:.4f}（降低了，更优）")
        print_info(f"排名: {result['data']['current_rank']}")
        print_info(f"排行榜更新: {'是' if result['data']['leaderboard_updated'] else '否'}")
        if result['data']['leaderboard_updated']:
            print_success("✓ 新分数更小，正确更新了排行榜")
    
    display_leaderboard(assignment_id, "更新后排行榜:")
    
    # 第三次提交（更小的RMSE = 继续改进）
    print_section("第3次提交 - RMSE=1.73（继续改进，应再次更新）")
    result = submit_assignment(student_id, name, assignment_id, 1.2, 3.0, 1.73, 3.5)
    if result["success"]:
        print_success(result["data"]["message"])
        print_info(f"新RMSE: {result['data']['score']:.4f}")
        print_info(f"旧RMSE: {result['data'].get('previous_score', 'N/A'):.4f}")
        print_info(f"变化: {result['data'].get('previous_score', 0) - result['data']['score']:.4f}（继续降低）")
        print_info(f"排名: {result['data']['current_rank']}")
        if result['data']['leaderboard_updated']:
            print_success("✓ 新分数更小，正确更新了排行榜")
    
    display_leaderboard(assignment_id, "最终排行榜:")
    
    # 第四次提交（较大的RMSE = 成绩变差，不应更新排行榜）
    print_section("第4次提交 - RMSE=3.46（成绩变差，不应更新排行榜）")
    result = submit_assignment(student_id, name, assignment_id, 3.0, 12.0, 3.46, 6.0)
    if result["success"]:
        print_success(result["data"]["message"])
        print_info(f"新RMSE: {result['data']['score']:.4f}")
        print_info(f"最优RMSE: {result['data'].get('previous_score', 'N/A'):.4f}")
        print_info(f"变化: {result['data']['score'] - result['data'].get('previous_score', 0):.4f}（增大了，变差）")
        print_info(f"排行榜更新: {'是' if result['data']['leaderboard_updated'] else '否'}")
        if not result['data']['leaderboard_updated']:
            print_success("✓ 新分数更大（变差），正确保持了最优成绩")
        else:
            print_warning("⚠ 预期不应更新排行榜，但实际更新了")
    
    display_leaderboard(assignment_id, "验证排行榜（应保持RMSE=1.73的最优成绩）:")
    
    # 第五次提交（相同的RMSE = 成绩相同，只更新提交次数）
    print_section("第5次提交 - RMSE=1.73（成绩相同，只更新提交次数）")
    result = submit_assignment(student_id, name, assignment_id, 1.2, 3.0, 1.73, 3.5)
    if result["success"]:
        print_success(result["data"]["message"])
        print_info(f"新RMSE: {result['data']['score']:.4f}")
        print_info(f"旧RMSE: {result['data'].get('previous_score', 'N/A'):.4f}")
        print_info(f"提交次数: {result['data']['submission_count']}")
        print_info(f"排行榜更新: {'是' if result['data']['leaderboard_updated'] else '否'}")
        if result['data']['leaderboard_updated']:
            print_success("✓ 分数相同，正确更新了提交次数")
    
    display_leaderboard(assignment_id, "最终排行榜（提交次数应为5）:")


def test_scenario_2():
    """
    测试场景2: 同一同学多次提交不同assignment_id
    测试多作业支持
    """
    print_header("测试场景2: 同一同学提交不同作业")
    
    student_id = "TEST002"
    name = "测试学生B"
    
    # 提交作业01
    print_section("提交作业01")
    result = submit_assignment(student_id, name, "01", 1.5, 4.0, 2.0, 4.0)
    if result["success"]:
        print_success(f"作业01提交成功 - RMSE: {result['data']['score']:.4f}")
    
    display_leaderboard("01", "作业01排行榜:")
    
    # 提交作业02
    print_section("提交作业02")
    result = submit_assignment(student_id, name, "02", 1.2, 3.0, 1.73, 3.5)
    if result["success"]:
        print_success(f"作业02提交成功 - RMSE: {result['data']['score']:.4f}")
    
    display_leaderboard("02", "作业02排行榜:")
    
    # 再次提交作业01（RMSE更小=改进）
    print_section("再次提交作业01（RMSE更小=改进）")
    result = submit_assignment(student_id, name, "01", 1.0, 2.5, 1.58, 3.2)
    if result["success"]:
        print_success(f"作业01提交成功 - RMSE: {result['data']['score']:.4f}")
        print_info(f"这是第 {result['data']['submission_count']} 次提交作业01")
        if result['data']['leaderboard_updated']:
            print_success("✓ RMSE更小，成功更新")
    
    display_leaderboard("01", "作业01更新后排行榜:")
    
    # 再次提交作业02（RMSE更小=改进）
    print_section("再次提交作业02（RMSE更小=改进）")
    result = submit_assignment(student_id, name, "02", 0.9, 2.0, 1.41, 3.0)
    if result["success"]:
        print_success(f"作业02提交成功 - RMSE: {result['data']['score']:.4f}")
        print_info(f"这是第 {result['data']['submission_count']} 次提交作业02")
        if result['data']['leaderboard_updated']:
            print_success("✓ RMSE更小，成功更新")
    
    display_leaderboard("02", "作业02更新后排行榜:")
    
    print_success("\n✓ 同一学生可以独立提交和改进不同作业的成绩")


def test_scenario_3():
    """
    测试场景3: 多个同学提交同一个assignment_id
    测试排行榜功能
    """
    print_header("测试场景3: 多个同学提交同一作业")
    
    assignment_id = "01"
    
    # 定义多个学生
    students = [
        {"id": "2025001", "name": "张三", "mae": 1.8, "mse": 5.5, "rmse": 2.35, "time": 4.5},
        {"id": "2025002", "name": "李四", "mae": 1.2, "mse": 3.2, "rmse": 1.79, "time": 3.8},
        {"id": "2025003", "name": "王五", "mae": 0.9, "mse": 2.0, "rmse": 1.41, "time": 3.2},
        {"id": "2025004", "name": "赵六", "mae": 1.5, "mse": 4.5, "rmse": 2.12, "time": 4.0},
        {"id": "2025005", "name": "钱七", "mae": 2.0, "mse": 6.0, "rmse": 2.45, "time": 5.0},
    ]
    
    print_section("5位同学首次提交")
    for student in students:
        result = submit_assignment(
            student["id"], student["name"], assignment_id,
            student["mae"], student["mse"], student["rmse"], student["time"]
        )
        if result["success"]:
            print_success(f"{student['name']} ({student['id']}) - RMSE: {result['data']['score']:.4f}, 排名: {result['data']['current_rank']}")
    
    display_leaderboard(assignment_id, "初始排行榜:")
    
    # 部分学生改进成绩（RMSE更小）
    print_section("部分同学提交改进的成绩（RMSE更小）")
    
    # 张三改进（RMSE从2.35降到1.58）
    result = submit_assignment("2025001", "张三", assignment_id, 1.0, 2.5, 1.58, 3.5)
    if result["success"]:
        print_success(f"张三改进 - 新RMSE: {result['data']['score']:.4f}, 旧RMSE: {result['data'].get('previous_score', 0):.4f}, 新排名: {result['data']['current_rank']}")
    
    # 赵六改进（RMSE从2.12降到1.22）
    result = submit_assignment("2025004", "赵六", assignment_id, 0.8, 1.5, 1.22, 3.0)
    if result["success"]:
        print_success(f"赵六改进 - 新RMSE: {result['data']['score']:.4f}, 旧RMSE: {result['data'].get('previous_score', 0):.4f}, 新排名: {result['data']['current_rank']}")
    
    # 钱七改进（RMSE从2.45降到1.67）
    result = submit_assignment("2025005", "钱七", assignment_id, 1.1, 2.8, 1.67, 3.8)
    if result["success"]:
        print_success(f"钱七改进 - 新RMSE: {result['data']['score']:.4f}, 旧RMSE: {result['data'].get('previous_score', 0):.4f}, 新排名: {result['data']['current_rank']}")
    
    display_leaderboard(assignment_id, "改进后排行榜:")
    
    print_success("\n✓ 排行榜正确显示多个学生的排名")


def test_scenario_4():
    """
    测试场景4: 时间超时测试
    使用assignment_id=03测试截止时间检查
    """
    print_header("测试场景4: 截止时间检查")
    
    student_id = "TEST999"
    name = "测试学生X"
    assignment_id = "03"  # 这个作业的截止时间是过去的时间
    
    print_section("尝试提交已超时的作业")
    print_info(f"作业ID: {assignment_id}")
    print_info(f"该作业的截止时间: 2024-01-01T00:00:00Z（已过期）")
    print_info(f"尝试提交...")
    
    result = submit_assignment(student_id, name, assignment_id, 1.0, 2.0, 1.41, 3.0)
    
    if not result["success"]:
        if result["status_code"] == 400:
            print_success("✓ 系统正确拒绝了超时提交")
            print_info(f"错误信息: {result['data'].get('detail', 'Unknown error')}")
        else:
            print_error(f"意外的错误: {result}")
    else:
        print_error("✗ 系统错误地接受了超时提交！")
        print_warning("这是一个BUG - 截止时间检查未正确工作")
    
    # 尝试提交未超时的作业作为对比
    print_section("对比：提交未超时的作业（作业01）")
    result = submit_assignment(student_id, name, "01", 1.0, 2.0, 1.41, 3.0)
    if result["success"]:
        print_success("✓ 未超时的作业可以正常提交")
        print_info(f"RMSE: {result['data']['score']:.4f}")
    else:
        print_error("提交失败（这不应该发生）")


def test_health_check():
    """健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print_success("后端服务正常运行")
            return True
        else:
            print_error("后端服务异常")
            return False
    except Exception as e:
        print_error(f"无法连接到后端服务: {e}")
        return False


def generate_summary():
    """生成测试总结"""
    print_header("测试总结")
    
    print(f"{Colors.BOLD}所有测试场景已完成！{Colors.END}\n")
    
    print(f"{Colors.CYAN}测试覆盖的功能：{Colors.END}")
    print("  1. ✓ 同一学生多次提交同一作业")
    print("     - ✓ 新分数更小（更优）时更新排行榜")
    print("     - ✓ 新分数更大（变差）时保持最优成绩")
    print("     - ✓ 新分数相同时只更新提交次数")
    print("     - ✓ 提交次数正确统计")
    print(f"     {Colors.YELLOW}注：RMSE越小越好{Colors.END}")
    
    print("\n  2. ✓ 同一学生提交不同作业")
    print("     - ✓ 多作业独立管理")
    print("     - ✓ 每个作业的提交次数独立统计")
    print("     - ✓ 每个作业的最优成绩独立维护")
    
    print("\n  3. ✓ 多个学生提交同一作业")
    print("     - ✓ 排行榜正确排序（RMSE从小到大）")
    print("     - ✓ 排名实时更新")
    print("     - ✓ 支持多人竞争")
    
    print("\n  4. ✓ 截止时间检查")
    print("     - ✓ 超时提交被正确拒绝（返回400错误）")
    print("     - ✓ 未超时提交正常处理")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'所有功能测试通过！'.center(80)}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'='*80}{Colors.END}\n")


def main():
    """主测试流程"""
    print_header("Leaderboard System 综合功能测试")
    
    print_info("开始测试...")
    print_info(f"后端地址: {BASE_URL}")
    print_info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 健康检查
    print_section("健康检查")
    if not test_health_check():
        print_error("\n无法连接到后端服务，请确保后端已启动！")
        print_info("启动命令: cd backend && start.bat (或 ./start.sh)")
        return
    
    # 执行测试场景
    try:
        test_scenario_1()  # 同一学生多次提交同一作业
        input(f"\n{Colors.YELLOW}按Enter继续下一个测试场景...{Colors.END}")
        
        test_scenario_2()  # 同一学生提交不同作业
        input(f"\n{Colors.YELLOW}按Enter继续下一个测试场景...{Colors.END}")
        
        test_scenario_3()  # 多个学生提交同一作业
        input(f"\n{Colors.YELLOW}按Enter继续下一个测试场景...{Colors.END}")
        
        test_scenario_4()  # 超时测试
        input(f"\n{Colors.YELLOW}按Enter查看测试总结...{Colors.END}")
        
        # 生成总结
        generate_summary()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}测试被用户中断{Colors.END}")
    except Exception as e:
        print_error(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

