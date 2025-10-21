#!/usr/bin/env python3
"""
测试备份和归档功能
"""

import os
import sys
from pathlib import Path

# 添加backend路径
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.backup_service import (
    ensure_backup_dirs,
    backup_to_checkpoint,
    archive_to_homework,
    cleanup_old_checkpoints
)


def test_manual_backup():
    """测试手动备份功能"""
    print("=" * 80)
    print("测试1: 手动备份到checkpoint")
    print("=" * 80)
    
    # 确保目录存在
    ensure_backup_dirs()
    print("✓ 备份目录已创建\n")
    
    # 执行备份
    timestamp = backup_to_checkpoint()
    print(f"\n✓ 备份完成，时间戳: {timestamp}")
    
    # 检查备份文件
    database_dir = Path(__file__).parent.parent / "backend" / "database"
    checkpoint_dir = database_dir / "checkpoint"
    
    submissions_backup = checkpoint_dir / f"submissions_{timestamp}.json"
    leaderboard_backup = checkpoint_dir / f"leaderboard_{timestamp}.json"
    
    if submissions_backup.exists():
        print(f"✓ submissions备份文件已创建: {submissions_backup.name}")
    else:
        print(f"❌ submissions备份文件未找到")
    
    if leaderboard_backup.exists():
        print(f"✓ leaderboard备份文件已创建: {leaderboard_backup.name}")
    else:
        print(f"❌ leaderboard备份文件未找到")


def test_archive_homework():
    """测试归档功能"""
    print("\n\n" + "=" * 80)
    print("测试2: 归档作业到homework")
    print("=" * 80)
    
    # 归档作业01
    timestamp = archive_to_homework("01")
    print(f"\n✓ 归档完成，时间戳: {timestamp}")
    
    # 检查归档文件
    database_dir = Path(__file__).parent.parent / "backend" / "database"
    homework_dir = database_dir / "homework"
    
    submissions_archive = homework_dir / f"submissions_01_{timestamp}.json"
    leaderboard_archive = homework_dir / f"leaderboard_01_{timestamp}.json"
    
    if submissions_archive.exists():
        print(f"✓ submissions归档文件已创建: {submissions_archive.name}")
    else:
        print(f"❌ submissions归档文件未找到")
    
    if leaderboard_archive.exists():
        print(f"✓ leaderboard归档文件已创建: {leaderboard_archive.name}")
    else:
        print(f"❌ leaderboard归档文件未找到")


def test_cleanup():
    """测试清理旧备份"""
    print("\n\n" + "=" * 80)
    print("测试3: 清理旧备份（保留7天内）")
    print("=" * 80)
    
    cleanup_old_checkpoints(keep_days=7)
    print("\n✓ 清理完成")


def show_backup_structure():
    """显示备份目录结构"""
    print("\n\n" + "=" * 80)
    print("当前备份目录结构:")
    print("=" * 80)
    
    database_dir = Path(__file__).parent.parent / "backend" / "database"
    
    print(f"\n📁 {database_dir.name}/")
    
    # checkpoint目录
    checkpoint_dir = database_dir / "checkpoint"
    if checkpoint_dir.exists():
        files = sorted(checkpoint_dir.glob("*.json"))
        print(f"  📁 checkpoint/ ({len(files)} 个文件)")
        for f in files[:10]:  # 只显示最近10个
            size = f.stat().st_size / 1024
            print(f"    📄 {f.name} ({size:.1f} KB)")
        if len(files) > 10:
            print(f"    ... 还有 {len(files) - 10} 个文件")
    
    # homework目录
    homework_dir = database_dir / "homework"
    if homework_dir.exists():
        files = sorted(homework_dir.glob("*.json"))
        print(f"  📁 homework/ ({len(files)} 个文件)")
        for f in files:
            size = f.stat().st_size / 1024
            print(f"    📄 {f.name} ({size:.1f} KB)")


def main():
    print("=" * 80)
    print("备份和归档功能测试")
    print("=" * 80)
    print("\n功能说明:")
    print("1. 定期备份: 每12小时自动备份到 database/checkpoint/")
    print("2. 归档作业: 到达截止日期后自动归档到 database/homework/")
    print("3. 自动清理: 删除7天前的checkpoint备份文件")
    print("=" * 80)
    
    input("\n按回车开始测试...")
    
    # 测试1: 手动备份
    test_manual_backup()
    input("\n按回车继续...")
    
    # 测试2: 归档作业
    test_archive_homework()
    input("\n按回车继续...")
    
    # 测试3: 清理旧备份
    test_cleanup()
    input("\n按回车继续...")
    
    # 显示目录结构
    show_backup_structure()
    
    print("\n\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)
    print("\n说明:")
    print("- checkpoint备份: 用于日常恢复，保留7天")
    print("- homework归档: 用于长期保存作业数据")
    print("- 后端启动时会自动执行一次备份")
    print("- 后端运行期间每12小时自动备份一次")
    print("=" * 80)


if __name__ == "__main__":
    main()

