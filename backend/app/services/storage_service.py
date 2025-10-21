import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# 数据库目录
DATABASE_DIR = Path(__file__).parent.parent.parent / "database"
SUBMISSIONS_FILE = DATABASE_DIR / "submissions.json"
LEADERBOARD_FILE = DATABASE_DIR / "leaderboard.json"
ASSIGNMENTS_FILE = DATABASE_DIR / "assignments.json"


def ensure_database_exists():
    """确保数据库目录和文件存在"""
    DATABASE_DIR.mkdir(exist_ok=True)
    
    # 初始化submissions文件
    if not SUBMISSIONS_FILE.exists():
        with open(SUBMISSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # 初始化leaderboard文件
    if not LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
    
    # 初始化assignments文件（包含作业配置）
    if not ASSIGNMENTS_FILE.exists():
        with open(ASSIGNMENTS_FILE, 'w', encoding='utf-8') as f:
            # 默认配置示例
            default_assignments = {
                "01": {
                    "assignment_id": "01",
                    "title": "作业1",
                    "deadline": "2025-12-31T23:59:59Z",
                    "weights": {
                        "MAE": 0.25,
                        "MSE": 0.25,
                        "RMSE": 0.25,
                        "Prediction_Time": 0.25
                    }
                }
            }
            json.dump(default_assignments, f, ensure_ascii=False, indent=2)


def get_assignment_config(assignment_id: str) -> Optional[Dict]:
    """
    获取作业配置
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        作业配置字典，如果不存在则返回None
    """
    ensure_database_exists()
    
    with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
        assignments = json.load(f)
    
    return assignments.get(assignment_id)


def is_deadline_passed(assignment_id: str) -> bool:
    """
    检查作业是否超过截止时间
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        是否超时
    """
    config = get_assignment_config(assignment_id)
    if not config:
        return False  # 如果配置不存在，默认未超时
    
    deadline_str = config.get("deadline")
    if not deadline_str:
        return False
    
    deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
    current_time = datetime.now(deadline.tzinfo)
    
    return current_time > deadline


def get_submission_count(student_id: str, assignment_id: str) -> int:
    """
    获取学生在指定作业的总提交次数
    
    Args:
        student_id: 学生ID
        assignment_id: 作业ID
        
    Returns:
        总提交次数
    """
    ensure_database_exists()
    
    with open(SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    count = sum(
        1 for s in submissions
        if s['student_info']['student_id'] == student_id
        and s['assignment_id'] == assignment_id
    )
    
    return count


def ww(student_id: str, assignment_id: str, date: Optional[str] = None) -> int:
    """
    获取学生在指定作业的当日提交次数
    
    Args:
        student_id: 学生ID
        assignment_id: 作业ID
        date: 日期字符串（YYYY-MM-DD格式），默认为今天（UTC）
        
    Returns:
        当日提交次数
    """
    ensure_database_exists()
    
    with open(SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    # 确定要检查的日期
    if date is None:
        target_date = datetime.utcnow().date()
    else:
        target_date = datetime.fromisoformat(date).date()
    
    count = 0
    for s in submissions:
        if (s['student_info']['student_id'] == student_id and 
            s['assignment_id'] == assignment_id):
            # 解析提交时间戳
            timestamp_str = s['submission_data']['timestamp']
            submission_datetime = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            submission_date = submission_datetime.date()
            
            # 检查是否在同一天
            if submission_date == target_date:
                count += 1
    
    return count


def save_submission(submission: Dict) -> None:
    """
    保存提交记录到历史
    
    Args:
        submission: 完整的提交记录
    """
    ensure_database_exists()
    
    with open(SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    submissions.append(submission)
    
    with open(SUBMISSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(submissions, f, ensure_ascii=False, indent=2)


def get_leaderboard(assignment_id: str) -> List[Dict]:
    """
    获取指定作业的排行榜
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        排行榜列表
    """
    ensure_database_exists()
    
    with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
        leaderboard_data = json.load(f)
    
    return leaderboard_data.get(assignment_id, [])


def update_leaderboard(assignment_id: str, leaderboard: List[Dict]) -> None:
    """
    更新排行榜
    
    Args:
        assignment_id: 作业ID
        leaderboard: 新的排行榜列表
    """
    ensure_database_exists()
    
    with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
        leaderboard_data = json.load(f)
    
    leaderboard_data[assignment_id] = leaderboard
    
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(leaderboard_data, f, ensure_ascii=False, indent=2)


def get_student_leaderboard_entry(
    student_id: str,
    assignment_id: str
) -> Optional[Dict]:
    """
    获取学生在排行榜中的记录
    
    Args:
        student_id: 学生ID
        assignment_id: 作业ID
        
    Returns:
        学生的排行榜记录，如果不存在返回None
    """
    leaderboard = get_leaderboard(assignment_id)
    
    for entry in leaderboard:
        if entry['student_info']['student_id'] == student_id:
            return entry
    
    return None

