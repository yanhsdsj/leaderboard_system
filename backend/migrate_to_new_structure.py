"""
数据迁移脚本：将旧的存储结构迁移到新的存储结构

旧结构：
- database/submissions.json (所有作业混在一起)
- database/leaderboard.json (按assignment_id分组的字典)
- database/checkpoint/*.json (混合备份)

新结构：
- database/submissions/submissions_{assignment_id}.json (每个作业独立文件)
- database/leaderboard/leaderboard_{assignment_id}.json (每个作业独立文件)
- database/checkpoint/submissions/{assignment_id}/*.json (按作业分组的备份)
- database/checkpoint/leaderboard/{assignment_id}/*.json (按作业分组的备份)
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# 数据库目录
DATABASE_DIR = Path(__file__).parent / "database"

# 旧文件路径
OLD_SUBMISSIONS_FILE = DATABASE_DIR / "submissions.json"
OLD_LEADERBOARD_FILE = DATABASE_DIR / "leaderboard.json"
OLD_CHECKPOINT_DIR = DATABASE_DIR / "checkpoint"

# 新目录路径
NEW_SUBMISSIONS_DIR = DATABASE_DIR / "submissions"
NEW_LEADERBOARD_DIR = DATABASE_DIR / "leaderboard"
NEW_CHECKPOINT_SUBMISSIONS_DIR = OLD_CHECKPOINT_DIR / "submissions"
NEW_CHECKPOINT_LEADERBOARD_DIR = OLD_CHECKPOINT_DIR / "leaderboard"

# 备份目录（保存旧文件）
BACKUP_DIR = DATABASE_DIR / "backup_old_structure"


def create_backup():
    """备份旧的数据文件"""
    print("\n" + "=" * 80)
    print("步骤1: 备份旧数据文件")
    print("=" * 80)
    
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_count = 0
    
    # 备份旧的submissions.json
    if OLD_SUBMISSIONS_FILE.exists():
        backup_file = BACKUP_DIR / f"submissions_backup_{timestamp}.json"
        shutil.copy2(OLD_SUBMISSIONS_FILE, backup_file)
        print(f"✓ 备份: {OLD_SUBMISSIONS_FILE.name} -> {backup_file.name}")
        backup_count += 1
    
    # 备份旧的leaderboard.json
    if OLD_LEADERBOARD_FILE.exists():
        backup_file = BACKUP_DIR / f"leaderboard_backup_{timestamp}.json"
        shutil.copy2(OLD_LEADERBOARD_FILE, backup_file)
        print(f"✓ 备份: {OLD_LEADERBOARD_FILE.name} -> {backup_file.name}")
        backup_count += 1
    
    # 备份旧的checkpoint目录
    if OLD_CHECKPOINT_DIR.exists():
        old_checkpoint_files = list(OLD_CHECKPOINT_DIR.glob("*.json"))
        if old_checkpoint_files:
            checkpoint_backup_dir = BACKUP_DIR / f"checkpoint_backup_{timestamp}"
            checkpoint_backup_dir.mkdir(exist_ok=True)
            
            for file in old_checkpoint_files:
                shutil.copy2(file, checkpoint_backup_dir / file.name)
                backup_count += 1
            
            print(f"✓ 备份: checkpoint/*.json -> {checkpoint_backup_dir.name}/ ({len(old_checkpoint_files)} 文件)")
    
    print(f"\n✓ 备份完成，共备份 {backup_count} 个文件")
    print(f"  备份位置: {BACKUP_DIR}")


def migrate_submissions():
    """迁移提交记录"""
    print("\n" + "=" * 80)
    print("步骤2: 迁移提交记录 (submissions)")
    print("=" * 80)
    
    if not OLD_SUBMISSIONS_FILE.exists():
        print("⚠️  未找到旧的submissions.json文件，跳过")
        return
    
    # 读取旧的submissions.json
    with open(OLD_SUBMISSIONS_FILE, 'r', encoding='utf-8') as f:
        all_submissions = json.load(f)
    
    print(f"✓ 读取旧文件: {len(all_submissions)} 条提交记录")
    
    # 按作业ID分组
    submissions_by_assignment = defaultdict(list)
    for submission in all_submissions:
        assignment_id = submission.get('assignment_id', 'unknown')
        submissions_by_assignment[assignment_id].append(submission)
    
    # 创建新目录
    NEW_SUBMISSIONS_DIR.mkdir(exist_ok=True)
    
    # 写入新文件
    for assignment_id, submissions in submissions_by_assignment.items():
        new_file = NEW_SUBMISSIONS_DIR / f"submissions_{assignment_id}.json"
        with open(new_file, 'w', encoding='utf-8') as f:
            json.dump(submissions, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 创建: {new_file.name} ({len(submissions)} 条记录)")
    
    print(f"\n✓ 提交记录迁移完成，共 {len(submissions_by_assignment)} 个作业")


def migrate_leaderboard():
    """迁移排行榜"""
    print("\n" + "=" * 80)
    print("步骤3: 迁移排行榜 (leaderboard)")
    print("=" * 80)
    
    if not OLD_LEADERBOARD_FILE.exists():
        print("⚠️  未找到旧的leaderboard.json文件，跳过")
        return
    
    # 读取旧的leaderboard.json
    with open(OLD_LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
        leaderboard_data = json.load(f)
    
    print(f"✓ 读取旧文件: {len(leaderboard_data)} 个作业的排行榜")
    
    # 创建新目录
    NEW_LEADERBOARD_DIR.mkdir(exist_ok=True)
    
    # 写入新文件（每个作业一个文件）
    for assignment_id, leaderboard in leaderboard_data.items():
        new_file = NEW_LEADERBOARD_DIR / f"leaderboard_{assignment_id}.json"
        with open(new_file, 'w', encoding='utf-8') as f:
            json.dump(leaderboard, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 创建: {new_file.name} ({len(leaderboard)} 名学生)")
    
    print(f"\n✓ 排行榜迁移完成，共 {len(leaderboard_data)} 个作业")


def migrate_checkpoint():
    """迁移备份文件"""
    print("\n" + "=" * 80)
    print("步骤4: 迁移备份文件 (checkpoint)")
    print("=" * 80)
    
    if not OLD_CHECKPOINT_DIR.exists():
        print("⚠️  未找到旧的checkpoint目录，跳过")
        return
    
    # 创建新的备份目录结构
    NEW_CHECKPOINT_SUBMISSIONS_DIR.mkdir(exist_ok=True)
    NEW_CHECKPOINT_LEADERBOARD_DIR.mkdir(exist_ok=True)
    
    # 处理旧的备份文件
    old_backup_files = list(OLD_CHECKPOINT_DIR.glob("*.json"))
    
    if not old_backup_files:
        print("⚠️  未找到旧的备份文件，跳过")
        return
    
    print(f"✓ 找到 {len(old_backup_files)} 个旧备份文件")
    
    submissions_count = 0
    leaderboard_count = 0
    
    for old_file in old_backup_files:
        filename = old_file.name
        
        # 处理submissions备份文件
        if filename.startswith("submissions_"):
            # 读取文件内容
            with open(old_file, 'r', encoding='utf-8') as f:
                try:
                    all_submissions = json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️  跳过损坏的文件: {filename}")
                    continue
            
            # 按作业ID分组
            submissions_by_assignment = defaultdict(list)
            for submission in all_submissions:
                assignment_id = submission.get('assignment_id', 'unknown')
                submissions_by_assignment[assignment_id].append(submission)
            
            # 提取时间戳（假设文件名格式为 submissions_YYYYMMDD_HHMMSS.json）
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                timestamp = '_'.join(parts[1:])  # YYYYMMDD_HHMMSS
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 为每个作业创建备份文件
            for assignment_id, submissions in submissions_by_assignment.items():
                assignment_dir = NEW_CHECKPOINT_SUBMISSIONS_DIR / assignment_id
                assignment_dir.mkdir(exist_ok=True)
                
                new_file = assignment_dir / f"submissions_{assignment_id}_{timestamp}.json"
                with open(new_file, 'w', encoding='utf-8') as f:
                    json.dump(submissions, f, ensure_ascii=False, indent=2)
                
                submissions_count += 1
            
            print(f"✓ 迁移: {filename} -> {len(submissions_by_assignment)} 个作业目录")
        
        # 处理leaderboard备份文件
        elif filename.startswith("leaderboard_"):
            # 读取文件内容
            with open(old_file, 'r', encoding='utf-8') as f:
                try:
                    leaderboard_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️  跳过损坏的文件: {filename}")
                    continue
            
            # 提取时间戳
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 3:
                timestamp = '_'.join(parts[1:])  # YYYYMMDD_HHMMSS
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 为每个作业创建备份文件
            for assignment_id, leaderboard in leaderboard_data.items():
                assignment_dir = NEW_CHECKPOINT_LEADERBOARD_DIR / assignment_id
                assignment_dir.mkdir(exist_ok=True)
                
                new_file = assignment_dir / f"leaderboard_{assignment_id}_{timestamp}.json"
                with open(new_file, 'w', encoding='utf-8') as f:
                    json.dump(leaderboard, f, ensure_ascii=False, indent=2)
                
                leaderboard_count += 1
            
            print(f"✓ 迁移: {filename} -> {len(leaderboard_data)} 个作业目录")
    
    print(f"\n✓ 备份文件迁移完成:")
    print(f"  - submissions备份: {submissions_count} 个文件")
    print(f"  - leaderboard备份: {leaderboard_count} 个文件")


def cleanup_old_files():
    """清理旧文件（可选）"""
    print("\n" + "=" * 80)
    print("步骤5: 清理旧文件")
    print("=" * 80)
    
    files_to_remove = []
    
    if OLD_SUBMISSIONS_FILE.exists():
        files_to_remove.append(OLD_SUBMISSIONS_FILE)
    
    if OLD_LEADERBOARD_FILE.exists():
        files_to_remove.append(OLD_LEADERBOARD_FILE)
    
    # 旧的checkpoint文件
    if OLD_CHECKPOINT_DIR.exists():
        for file in OLD_CHECKPOINT_DIR.glob("*.json"):
            files_to_remove.append(file)
    
    if not files_to_remove:
        print("✓ 没有需要清理的旧文件")
        return
    
    print(f"\n找到 {len(files_to_remove)} 个旧文件:")
    for file in files_to_remove:
        print(f"  - {file.relative_to(DATABASE_DIR)}")
    
    print("\n⚠️  这些文件已经备份到:", BACKUP_DIR)
    response = input("\n是否删除这些旧文件? (yes/no): ").strip().lower()
    
    if response == 'yes':
        for file in files_to_remove:
            file.unlink()
            print(f"✓ 删除: {file.name}")
        print(f"\n✓ 已删除 {len(files_to_remove)} 个旧文件")
    else:
        print("\n✓ 保留旧文件（你可以稍后手动删除）")


def verify_migration():
    """验证迁移结果"""
    print("\n" + "=" * 80)
    print("步骤6: 验证迁移结果")
    print("=" * 80)
    
    # 检查新的submissions目录
    if NEW_SUBMISSIONS_DIR.exists():
        submissions_files = list(NEW_SUBMISSIONS_DIR.glob("submissions_*.json"))
        print(f"✓ 新的submissions目录: {len(submissions_files)} 个作业文件")
        for file in submissions_files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  - {file.name}: {len(data)} 条记录")
    else:
        print("⚠️  新的submissions目录不存在")
    
    # 检查新的leaderboard目录
    if NEW_LEADERBOARD_DIR.exists():
        leaderboard_files = list(NEW_LEADERBOARD_DIR.glob("leaderboard_*.json"))
        print(f"\n✓ 新的leaderboard目录: {len(leaderboard_files)} 个作业文件")
        for file in leaderboard_files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  - {file.name}: {len(data)} 名学生")
    else:
        print("⚠️  新的leaderboard目录不存在")
    
    # 检查新的checkpoint目录结构
    if NEW_CHECKPOINT_SUBMISSIONS_DIR.exists():
        assignment_dirs = [d for d in NEW_CHECKPOINT_SUBMISSIONS_DIR.iterdir() if d.is_dir()]
        print(f"\n✓ 新的checkpoint/submissions目录: {len(assignment_dirs)} 个作业目录")
        for assignment_dir in assignment_dirs:
            backup_files = list(assignment_dir.glob("*.json"))
            print(f"  - {assignment_dir.name}/: {len(backup_files)} 个备份文件")
    
    if NEW_CHECKPOINT_LEADERBOARD_DIR.exists():
        assignment_dirs = [d for d in NEW_CHECKPOINT_LEADERBOARD_DIR.iterdir() if d.is_dir()]
        print(f"\n✓ 新的checkpoint/leaderboard目录: {len(assignment_dirs)} 个作业目录")
        for assignment_dir in assignment_dirs:
            backup_files = list(assignment_dir.glob("*.json"))
            print(f"  - {assignment_dir.name}/: {len(backup_files)} 个备份文件")


def main():
    """主迁移流程"""
    print("\n")
    print("=" * 80)
    print(" 数据迁移脚本：旧存储结构 -> 新存储结构")
    print("=" * 80)
    print("\n此脚本会将数据从旧的存储结构迁移到新的存储结构。")
    print("旧文件会被备份到:", BACKUP_DIR)
    print("\n请确保：")
    print("  1. 后端服务已停止")
    print("  2. 已经备份了重要数据")
    print()
    
    response = input("是否继续迁移? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ 迁移已取消")
        return
    
    try:
        # 执行迁移步骤
        create_backup()
        migrate_submissions()
        migrate_leaderboard()
        migrate_checkpoint()
        verify_migration()
        cleanup_old_files()
        
        print("\n" + "=" * 80)
        print(" ✓ 迁移完成!")
        print("=" * 80)
        print("\n后续步骤:")
        print("  1. 验证新的数据文件是否正确")
        print("  2. 启动后端服务测试功能")
        print("  3. 如果一切正常，可以删除备份目录:", BACKUP_DIR)
        print()
        
    except Exception as e:
        print(f"\n❌ 迁移过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n请检查错误，旧数据已备份到:", BACKUP_DIR)


if __name__ == "__main__":
    main()

