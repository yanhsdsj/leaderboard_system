import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import asyncio


# 数据库目录结构
DATABASE_DIR = Path(__file__).parent.parent.parent / "database"
ASSIGNMENTS_FILE = DATABASE_DIR / "assignments.json"

SUBMISSIONS_DIR = DATABASE_DIR / "submissions"
LEADERBOARD_DIR = DATABASE_DIR / "leaderboard"

# 备份目录
CHECKPOINT_DIR = DATABASE_DIR / "checkpoint"
CHECKPOINT_SUBMISSIONS_DIR = CHECKPOINT_DIR / "submissions"
CHECKPOINT_LEADERBOARD_DIR = CHECKPOINT_DIR / "leaderboard"
HOMEWORK_DIR = DATABASE_DIR / "homework"


def ensure_backup_dirs():
    """确保备份目录存在"""
    CHECKPOINT_DIR.mkdir(exist_ok=True)
    CHECKPOINT_SUBMISSIONS_DIR.mkdir(exist_ok=True)
    CHECKPOINT_LEADERBOARD_DIR.mkdir(exist_ok=True)
    HOMEWORK_DIR.mkdir(exist_ok=True)


def get_checkpoint_submission_dir(assignment_id: str) -> Path:
    """
    获取指定作业的提交记录备份目录
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        备份目录路径
    """
    checkpoint_dir = CHECKPOINT_SUBMISSIONS_DIR / assignment_id
    checkpoint_dir.mkdir(exist_ok=True)
    return checkpoint_dir


def get_checkpoint_leaderboard_dir(assignment_id: str) -> Path:
    """
    获取指定作业的排行榜备份目录
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        备份目录路径
    """
    checkpoint_dir = CHECKPOINT_LEADERBOARD_DIR / assignment_id
    checkpoint_dir.mkdir(exist_ok=True)
    return checkpoint_dir


def backup_assignment_to_checkpoint(assignment_id: str) -> str:
    """
    备份指定作业的数据到checkpoint目录
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        时间戳字符串
    """
    ensure_backup_dirs()
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # 备份submissions
    submissions_file = SUBMISSIONS_DIR / f"submissions_{assignment_id}.json"
    if submissions_file.exists():
        checkpoint_dir = get_checkpoint_submission_dir(assignment_id)
        backup_file = checkpoint_dir / f"submissions_{assignment_id}_{timestamp}.json"
        shutil.copy2(submissions_file, backup_file)
        print(f"✓ 备份作业 [{assignment_id}] submissions -> {backup_file.name}")
    
    # 备份leaderboard
    leaderboard_file = LEADERBOARD_DIR / f"leaderboard_{assignment_id}.json"
    if leaderboard_file.exists():
        checkpoint_dir = get_checkpoint_leaderboard_dir(assignment_id)
        backup_file = checkpoint_dir / f"leaderboard_{assignment_id}_{timestamp}.json"
        shutil.copy2(leaderboard_file, backup_file)
        print(f"✓ 备份作业 [{assignment_id}] leaderboard -> {backup_file.name}")
    
    return timestamp


def backup_to_checkpoint():
    """
    将所有作业的submissions和leaderboard备份到checkpoint目录
    """
    ensure_backup_dirs()
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backed_up_count = 0
    
    # 遍历所有作业的提交文件
    if SUBMISSIONS_DIR.exists():
        for submissions_file in SUBMISSIONS_DIR.glob("submissions_*.json"):
            # 从文件名提取作业ID：submissions_{assignment_id}.json
            filename = submissions_file.stem  # 去掉 .json
            if filename.startswith("submissions_"):
                assignment_id = filename[len("submissions_"):]
                backup_assignment_to_checkpoint(assignment_id)
                backed_up_count += 1
    
    if backed_up_count > 0:
        print(f"✓ 共备份 {backed_up_count} 个作业的数据")
    else:
        print("⚠️  没有找到需要备份的作业数据")
    
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
    
    # 归档submissions（整个文件）
    submissions_file = SUBMISSIONS_DIR / f"submissions_{assignment_id}.json"
    if submissions_file.exists():
        with open(submissions_file, 'r', encoding='utf-8') as f:
            assignment_submissions = json.load(f)
        
        # 保存到homework目录
        archive_submissions = HOMEWORK_DIR / f"submissions_{assignment_id}_{timestamp}.json"
        with open(archive_submissions, 'w', encoding='utf-8') as f:
            json.dump(assignment_submissions, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 归档作业 [{title}] submissions -> {archive_submissions.name}")
        print(f"  共 {len(assignment_submissions)} 条提交记录")
    
    # 归档leaderboard（整个文件）
    leaderboard_file = LEADERBOARD_DIR / f"leaderboard_{assignment_id}.json"
    if leaderboard_file.exists():
        with open(leaderboard_file, 'r', encoding='utf-8') as f:
            assignment_leaderboard = json.load(f)
        
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
    
    # 清理submissions备份
    if CHECKPOINT_SUBMISSIONS_DIR.exists():
        for assignment_dir in CHECKPOINT_SUBMISSIONS_DIR.iterdir():
            if assignment_dir.is_dir():
                for file in assignment_dir.glob("*.json"):
                    file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    days_old = (current_time - file_mtime).days
                    
                    if days_old > keep_days:
                        file.unlink()
                        deleted_count += 1
                        print(f"✓ 删除旧备份: {assignment_dir.name}/{file.name} (已存在 {days_old} 天)")
    
    # 清理leaderboard备份
    if CHECKPOINT_LEADERBOARD_DIR.exists():
        for assignment_dir in CHECKPOINT_LEADERBOARD_DIR.iterdir():
            if assignment_dir.is_dir():
                for file in assignment_dir.glob("*.json"):
                    file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    days_old = (current_time - file_mtime).days
                    
                    if days_old > keep_days:
                        file.unlink()
                        deleted_count += 1
                        print(f"✓ 删除旧备份: {assignment_dir.name}/{file.name} (已存在 {days_old} 天)")
    
    if deleted_count > 0:
        print(f"✓ 共清理 {deleted_count} 个旧备份文件")
    else:
        print(f"✓ 没有需要清理的旧备份文件（保留最近 {keep_days} 天）")


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


def get_all_backups_for_assignment(assignment_id: str) -> Dict[str, List[str]]:
    """
    获取指定作业的所有备份文件列表
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        包含submissions和leaderboard备份列表的字典
    """
    result = {
        "submissions": [],
        "leaderboard": []
    }
    
    # 获取submissions备份
    submissions_backup_dir = CHECKPOINT_SUBMISSIONS_DIR / assignment_id
    if submissions_backup_dir.exists():
        for file in sorted(submissions_backup_dir.glob("*.json"), reverse=True):
            result["submissions"].append(file.name)
    
    # 获取leaderboard备份
    leaderboard_backup_dir = CHECKPOINT_LEADERBOARD_DIR / assignment_id
    if leaderboard_backup_dir.exists():
        for file in sorted(leaderboard_backup_dir.glob("*.json"), reverse=True):
            result["leaderboard"].append(file.name)
    
    return result
