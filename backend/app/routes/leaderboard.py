from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..models.submission import LeaderboardEntry
from ..services.leaderboard_service import get_ranked_leaderboard

router = APIRouter(prefix="/api", tags=["leaderboard"])


@router.get("/leaderboard/{assignment_id}")
async def get_leaderboard(assignment_id: str):
    """
    获取指定作业的排行榜及配置信息
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        包含排行榜列表和作业配置的字典
    """
    # 验证作业ID是否存在
    from ..services.storage_service import get_assignment_config
    
    assignment_config = get_assignment_config(assignment_id)
    if assignment_config is None:
        raise HTTPException(
            status_code=404,
            detail=f"无效的作业ID：{assignment_id}，该作业不存在"
        )
    
    try:
        leaderboard = get_ranked_leaderboard(assignment_id)
        return {
            "leaderboard": leaderboard,
            "config": assignment_config
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取排行榜失败: {str(e)}"
        )


@router.get("/leaderboard")
async def get_all_leaderboards():
    """
    获取所有作业的排行榜
    Returns:
        所有排行榜的字典
    """
    try:
        from ..services.storage_service import get_all_assignment_ids, get_leaderboard
        
        # 获取所有作业ID
        assignment_ids = get_all_assignment_ids()
        
        # 为每个作业获取排行榜
        result = {}
        for assignment_id in assignment_ids:
            leaderboard = get_leaderboard(assignment_id)
            
            # 为每个排行榜添加排名
            ranked_leaderboard = []
            for idx, entry in enumerate(leaderboard):
                ranked_entry = entry.copy()
                ranked_entry['rank'] = idx + 1
                ranked_leaderboard.append(ranked_entry)
            result[assignment_id] = ranked_leaderboard
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取所有排行榜失败: {str(e)}"
        )


@router.get("/submissions/{student_id}/{assignment_id}")
async def get_student_submissions(student_id: str, assignment_id: str):
    """
    获取指定学生在指定作业的所有提交记录
    
    Args:
        student_id: 学生ID
        assignment_id: 作业ID
        
    Returns:
        该学生的所有提交记录（按时间倒序）
    """
    # 验证作业ID是否存在
    from ..services.storage_service import get_assignment_config
    
    assignment_config = get_assignment_config(assignment_id)
    if assignment_config is None:
        raise HTTPException(
            status_code=404,
            detail=f"无效的作业ID：{assignment_id}，该作业不存在"
        )
    
    try:
        from ..services.storage_service import get_all_submissions_for_assignment
        
        # 获取该作业的所有提交记录
        all_submissions = get_all_submissions_for_assignment(assignment_id)
        
        # 筛选该学生的提交记录
        student_submissions = [
            sub for sub in all_submissions
            if sub['student_info']['student_id'] == student_id
        ]
        
        # 按时间倒序排列
        student_submissions.sort(
            key=lambda x: x['submission_data']['timestamp'],
            reverse=True
        )
        
        return student_submissions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取提交记录失败: {str(e)}"
        )


@router.get("/assignments")
async def get_all_assignments() -> Dict:
    """
    获取所有作业配置
    
    Returns:
        所有作业的配置信息
    """
    try:
        from ..services.storage_service import ASSIGNMENTS_FILE, ensure_database_exists
        import json
        
        ensure_database_exists()
        
        with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
            assignments = json.load(f)
        
        return assignments
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取作业配置失败: {str(e)}"
        )


@router.get("/active-assignment")
async def get_active_assignment():
    """
    获取当前活跃的作业ID（未过截止时间的第一个作业）
    
    Returns:
        {"assignment_id": "02"} 或 {"assignment_id": null} 如果所有作业都已截止
    """
    try:
        from ..services.storage_service import get_assignment_config, ASSIGNMENTS_FILE
        from datetime import datetime
        import json
        
        # 读取所有作业配置
        with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
            all_assignments = json.load(f)
        
        current_time = datetime.utcnow()
        
        # 找出所有未截止的作业，并按作业ID排序
        active_assignments = []
        for assignment_id, config in all_assignments.items():
            if 'deadline' in config:
                # 移除时区信息进行比较
                deadline_str = config['deadline'].replace('Z', '')
                deadline = datetime.fromisoformat(deadline_str)
                if current_time < deadline:
                    active_assignments.append(assignment_id)
        
        # 对作业ID进行排序（数字优先，然后字母）
        active_assignments.sort()
        
        # 返回第一个活跃的作业，如果没有则返回 None
        return {
            "assignment_id": active_assignments[0] if active_assignments else None,
            "all_active": active_assignments
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取活跃作业失败: {str(e)}"
        )


@router.get("/students-without-submission/{assignment_id}")
async def get_students_without_submission(assignment_id: str):
    """
    获取未提交作业的学生列表
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        未提交学生的学号列表
    """
    # 验证作业ID是否存在
    from ..services.storage_service import get_assignment_config
    from pathlib import Path
    
    assignment_config = get_assignment_config(assignment_id)
    if assignment_config is None:
        raise HTTPException(
            status_code=404,
            detail=f"无效的作业ID：{assignment_id}，该作业不存在"
        )
    
    try:
        from ..services.storage_service import ensure_database_exists
        import json
        
        ensure_database_exists()
        
        # 读取选课名单 list.json
        list_file = Path(__file__).parent.parent.parent.parent / "list.json"
        all_student_ids = set()
        
        if list_file.exists():
            with open(list_file, 'r', encoding='utf-8') as f:
                students = json.load(f)
                for student in students:
                    # 将学号转换为字符串
                    all_student_ids.add(str(student['学号']))
        
        # 获取已提交的学生
        leaderboard = get_ranked_leaderboard(assignment_id)
        submitted_student_ids = set(entry['student_info']['student_id'] for entry in leaderboard)
        
        # 找出未提交的学生
        not_submitted = sorted(list(all_student_ids - submitted_student_ids))
        
        return {
            "assignment_id": assignment_id,
            "count": len(not_submitted),
            "student_ids": not_submitted
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取未提交学生列表失败: {str(e)}"
        )

