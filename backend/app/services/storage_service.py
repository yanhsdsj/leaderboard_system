import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# 数据库目录结构
DATABASE_DIR = Path(__file__).parent.parent.parent / "database"
ASSIGNMENTS_FILE = DATABASE_DIR / "assignments.json"

# 新的目录结构
SUBMISSIONS_DIR = DATABASE_DIR / "submissions"
LEADERBOARD_DIR = DATABASE_DIR / "leaderboard"
CHECKPOINT_DIR = DATABASE_DIR / "checkpoint"
CHECKPOINT_SUBMISSIONS_DIR = CHECKPOINT_DIR / "submissions"
CHECKPOINT_LEADERBOARD_DIR = CHECKPOINT_DIR / "leaderboard"


def get_submissions_file(assignment_id: str) -> Path:
    """
    获取指定作业的提交记录文件路径
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        提交记录文件路径
    """
    return SUBMISSIONS_DIR / f"submissions_{assignment_id}.json"


def get_leaderboard_file(assignment_id: str) -> Path:
    """
    获取指定作业的排行榜文件路径
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        排行榜文件路径
    """
    return LEADERBOARD_DIR / f"leaderboard_{assignment_id}.json"


def ensure_database_exists():
    """确保数据库目录和文件存在"""
    # 创建主目录结构
    DATABASE_DIR.mkdir(exist_ok=True)
    SUBMISSIONS_DIR.mkdir(exist_ok=True)
    LEADERBOARD_DIR.mkdir(exist_ok=True)
    CHECKPOINT_DIR.mkdir(exist_ok=True)
    CHECKPOINT_SUBMISSIONS_DIR.mkdir(exist_ok=True)
    CHECKPOINT_LEADERBOARD_DIR.mkdir(exist_ok=True)
    
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


def ensure_assignment_files_exist(assignment_id: str):
    """
    确保指定作业的数据文件存在
    
    Args:
        assignment_id: 作业ID
    """
    ensure_database_exists()
    
    # 确保提交记录文件存在
    submissions_file = get_submissions_file(assignment_id)
    if not submissions_file.exists():
        with open(submissions_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # 确保排行榜文件存在
    leaderboard_file = get_leaderboard_file(assignment_id)
    if not leaderboard_file.exists():
        with open(leaderboard_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)


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
    ensure_assignment_files_exist(assignment_id)
    
    submissions_file = get_submissions_file(assignment_id)
    with open(submissions_file, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    count = sum(
        1 for s in submissions
        if s['student_info']['student_id'] == student_id
    )
    
    return count


def get_daily_submission_count(student_id: str, assignment_id: str, date: Optional[str] = None) -> int:
    """
    获取学生在指定作业的当日提交次数
    
    Args:
        student_id: 学生ID
        assignment_id: 作业ID
        date: 日期字符串（YYYY-MM-DD格式），默认为今天（UTC）
        
    Returns:
        当日提交次数
    """
    ensure_assignment_files_exist(assignment_id)
    
    submissions_file = get_submissions_file(assignment_id)
    with open(submissions_file, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    # 确定要检查的日期
    if date is None:
        target_date = datetime.utcnow().date()
    else:
        target_date = datetime.fromisoformat(date).date()
    
    count = 0
    for s in submissions:
        if s['student_info']['student_id'] == student_id:
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
    assignment_id = submission.get('assignment_id')
    if not assignment_id:
        raise ValueError("提交记录缺少 assignment_id")
    
    ensure_assignment_files_exist(assignment_id)
    
    submissions_file = get_submissions_file(assignment_id)
    with open(submissions_file, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    submissions.append(submission)
    
    with open(submissions_file, 'w', encoding='utf-8') as f:
        json.dump(submissions, f, ensure_ascii=False, indent=2)


def get_leaderboard(assignment_id: str) -> List[Dict]:
    """
    获取指定作业的排行榜
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        排行榜列表
    """
    ensure_assignment_files_exist(assignment_id)
    
    leaderboard_file = get_leaderboard_file(assignment_id)
    with open(leaderboard_file, 'r', encoding='utf-8') as f:
        leaderboard = json.load(f)
    
    return leaderboard


def update_leaderboard(assignment_id: str, leaderboard: List[Dict]) -> None:
    """
    更新排行榜
    
    Args:
        assignment_id: 作业ID
        leaderboard: 新的排行榜列表
    """
    ensure_assignment_files_exist(assignment_id)
    
    leaderboard_file = get_leaderboard_file(assignment_id)
    with open(leaderboard_file, 'w', encoding='utf-8') as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)


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


def get_student_registered_info(student_id: str) -> Optional[Dict]:
    """
    获取学生首次注册时的完整信息
    
    从所有作业的提交记录中查找该学生ID的首次提交，返回当时的student_info
    这些信息（student_id, name, nickname）将作为该学生ID的唯一绑定信息，不允许修改
    
    Args:
        student_id: 学生ID
        
    Returns:
        学生的注册信息字典（包含student_id, name, nickname），如果学生从未提交则返回None
    """
    ensure_database_exists()
    
    # 遍历所有作业的提交文件
    if not SUBMISSIONS_DIR.exists():
        return None
    
    # 收集所有提交记录（带时间戳）
    all_submissions = []
    
    for submissions_file in SUBMISSIONS_DIR.glob("submissions_*.json"):
        try:
            with open(submissions_file, 'r', encoding='utf-8') as f:
                submissions = json.load(f)
                
            # 查找该学生的提交
            for submission in submissions:
                if submission['student_info']['student_id'] == student_id:
                    all_submissions.append(submission)
        except (json.JSONDecodeError, KeyError):
            # 跳过损坏的文件
            continue
    
    if not all_submissions:
        return None
    
    # 按时间戳排序，找到最早的提交
    all_submissions.sort(key=lambda s: s['submission_data']['timestamp'])
    
    return all_submissions[0]['student_info']


def get_all_assignment_ids() -> List[str]:
    """
    获取所有已有提交记录的作业ID列表
    
    Returns:
        作业ID列表
    """
    ensure_database_exists()
    
    assignment_ids = []
    
    if SUBMISSIONS_DIR.exists():
        for submissions_file in SUBMISSIONS_DIR.glob("submissions_*.json"):
            # 从文件名提取作业ID：submissions_{assignment_id}.json
            filename = submissions_file.stem  # 去掉 .json
            if filename.startswith("submissions_"):
                assignment_id = filename[len("submissions_"):]
                assignment_ids.append(assignment_id)
    
    return sorted(assignment_ids)


def get_all_submissions_for_assignment(assignment_id: str) -> List[Dict]:
    """
    获取指定作业的所有提交记录
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        提交记录列表
    """
    ensure_assignment_files_exist(assignment_id)
    
    submissions_file = get_submissions_file(assignment_id)
    with open(submissions_file, 'r', encoding='utf-8') as f:
        submissions = json.load(f)
    
    return submissions
