import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import asyncio


# 数据库目录
DATABASE_DIR = Path(__file__).parent.parent.parent / "database"
SUBMISSIONS_FILE = DATABASE_DIR / "submissions.json"
LEADERBOARD_FILE = DATABASE_DIR / "leaderboard.json"
ASSIGNMENTS_FILE = DATABASE_DIR / "assignments.json"

# 备份目录
CHECKPOINT_DIR = DATABASE_DIR / "checkpoint"
HOMEWORK_DIR = DATABASE_DIR / "homework"


def ensure_backup_dirs():
    """确保备份目录存在"""
    CHECKPOINT_DIR.mkdir(exist_ok=True)
    HOMEWORK_DIR.mkdir(exist_ok=True)


def backup_to_checkpoint():
    """
    将submissions和leaderboard备份到checkpoint目录
    文件名格式: submissions_YYYYMMDD_HHMMSS.json
    """
    ensure_backup_dirs()
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # 备份submissions
    if SUBMISSIONS_FILE.exists():
        backup_submissions = CHECKPOINT_DIR / f"submissions_{timestamp}.json"
        shutil.copy2(SUBMISSIONS_FILE, backup_submissions)
        print(f"✓ 备份submissions -> {backup_submissions.name}")
    
    # 备份leaderboard
    if LEADERBOARD_FILE.exists():
        backup_leaderboard = CHECKPOINT_DIR / f"leaderboard_{timestamp}.json"
        shutil.copy2(LEADERBOARD_FILE, backup_leaderboard)
        print(f"✓ 备份leaderboard -> {backup_leaderboard.name}")
    
    return timestamp


def archive_to_homework(assignment_id: str):
    """
    将指定作业的submissions和leaderboard归档到homework目录
    
    Args:
        assignment_id: 作业ID
    """
    ensure_backup_dirs()
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # 读取作业配置
    if ASSIGNMENTS_FILE.exists():
        with open(ASSIGNMENTS_FILE, 'r', encoding='utf-8') as f:
            assignments = json.load(f)
            assignment_config = assignments.get(assignment_id, {})
            title = assignment_config.get('title', assignment_id)
    else:
        title = assignment_id
    
    # 归档submissions（只保存该作业的提交）
    if SUBMISSIONS_FILE.exists():
        with open(SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
            all_submissions = json.load(f)
        
        # 过滤出该作业的提交
        assignment_submissions = [
            s for s in all_submissions 
            if s.get('assignment_id') == assignment_id
        ]
        
        # 保存到homework目录
        archive_submissions = HOMEWORK_DIR / f"submissions_{assignment_id}_{timestamp}.json"
        with open(archive_submissions, 'w', encoding='utf-8') as f:
            json.dump(assignment_submissions, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 归档作业 [{title}] submissions -> {archive_submissions.name}")
        print(f"  共 {len(assignment_submissions)} 条提交记录")
    
    # 归档leaderboard（只保存该作业的排行榜）
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            all_leaderboards = json.load(f)
        
        # 获取该作业的排行榜
        assignment_leaderboard = all_leaderboards.get(assignment_id, [])
        
        # 保存到homework目录
        archive_leaderboard = HOMEWORK_DIR / f"leaderboard_{assignment_id}_{timestamp}.json"
        with open(archive_leaderboard, 'w', encoding='utf-8') as f:
            json.dump(assignment_leaderboard, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 归档作业 [{title}] leaderboard -> {archive_leaderboard.name}")
        print(f"  共 {len(assignment_leaderboard)} 名学生")
    
    return timestamp


def cleanup_old_checkpoints(keep_days: int = 7):
    """
    清理旧的checkpoint备份文件（保留最近N天）
    
    Args:
        keep_days: 保留天数
    """
    if not CHECKPOINT_DIR.exists():
        return
    
    current_time = datetime.utcnow()
    deleted_count = 0
    
    for file in CHECKPOINT_DIR.glob("*.json"):
        # 文件修改时间
        file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
        days_old = (current_time - file_mtime).days
        
        if days_old > keep_days:
            file.unlink()
            deleted_count += 1
            print(f"✓ 删除旧备份: {file.name} (已存在 {days_old} 天)")
    
    if deleted_count > 0:
        print(f"✓ 共清理 {deleted_count} 个旧备份文件")


async def periodic_backup_task():
    """
    定期备份任务，每12小时执行一次
    """
    while True:
        try:
            print("\n" + "=" * 60)
            print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] 开始定期备份...")
            print("=" * 60)
            
            # 执行备份
            backup_to_checkpoint()
            
            # 清理7天前的旧备份
            cleanup_old_checkpoints(keep_days=7)
            
            print("=" * 60)
            print(f"✓ 定期备份完成，下次备份时间: 12小时后")
            print("=" * 60 + "\n")
            
        except Exception as e:
            print(f"❌ 备份任务出错: {str(e)}")
        
        # 等待12小时 (12 * 60 * 60 = 43200秒)
        await asyncio.sleep(43200)


# 记录已归档的作业，避免重复归档
_archived_assignments = set()


def check_and_archive_deadline(assignment_id: str, deadline_str: str):
    """
    检查作业是否刚过截止时间，如果是则归档
    
    Args:
        assignment_id: 作业ID
        deadline_str: 截止时间字符串
    """
    global _archived_assignments
    
    # 如果已经归档过，跳过
    if assignment_id in _archived_assignments:
        return
    
    try:
        # 解析截止时间
        deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        current_time = datetime.now(deadline.tzinfo)
        
        # 检查是否刚过截止时间（在截止时间后的24小时内）
        time_since_deadline = (current_time - deadline).total_seconds()
        
        # 如果已过截止时间，且在24小时内（避免老作业重复归档）
        if 0 < time_since_deadline < 86400:
            print(f"\n⚠️  作业 [{assignment_id}] 已过截止时间，开始归档...")
            archive_to_homework(assignment_id)
            _archived_assignments.add(assignment_id)
            print(f"✓ 作业 [{assignment_id}] 归档完成\n")
        # 如果过期超过24小时，也标记为已归档（避免每次都检查）
        elif time_since_deadline >= 86400:
            _archived_assignments.add(assignment_id)
            
    except Exception as e:
        print(f"❌ 检查归档时出错: {str(e)}")


def get_archived_assignments() -> set:
    """
    获取已归档的作业ID集合
    """
    global _archived_assignments
    return _archived_assignments.copy()

