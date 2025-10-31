"""
测试新的存储结构

验证新的存储系统是否正常工作
"""

import sys
from pathlib import Path

# 添加项目路径到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.storage_service import (
    ensure_database_exists,
    get_assignment_config,
    save_submission,
    get_leaderboard,
    update_leaderboard,
    get_submission_count,
    get_daily_submission_count,
    get_student_registered_info,
    get_all_assignment_ids
)
from datetime import datetime


def test_basic_storage():
    """测试基本存储功能"""
    print("\n" + "=" * 80)
    print("测试1: 基本存储功能")
    print("=" * 80)
    
    # 确保数据库存在
    ensure_database_exists()
    print("✓ 数据库目录结构创建成功")
    
    # 测试作业配置读取
    config = get_assignment_config("01")
    if config:
        print(f"✓ 读取作业配置成功: {config.get('title', 'N/A')}")
    else:
        print("⚠️  未找到作业01的配置")


def test_submissions():
    """测试提交记录功能"""
    print("\n" + "=" * 80)
    print("测试2: 提交记录功能")
    print("=" * 80)
    
    test_assignment_id = "test_01"
    test_student_id = "test_student_001"
    
    # 创建测试提交
    test_submission = {
        "student_info": {
            "student_id": test_student_id,
            "name": "测试学生",
            "nickname": "测试昵称"
        },
        "assignment_id": test_assignment_id,
        "submission_data": {
            "metrics": {
                "MAE": 0.5,
                "MSE": 0.3,
                "RMSE": 0.4,
                "Prediction_Time": 0.1
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "submission_count": 1,
            "checksums": {},
            "files": {}
        }
    }
    
    # 保存提交
    try:
        save_submission(test_submission)
        print(f"✓ 保存测试提交成功: {test_assignment_id}")
    except Exception as e:
        print(f"❌ 保存测试提交失败: {e}")
        return
    
    # 获取提交次数
    count = get_submission_count(test_student_id, test_assignment_id)
    print(f"✓ 获取提交次数: {count}")
    
    # 获取每日提交次数
    daily_count = get_daily_submission_count(test_student_id, test_assignment_id)
    print(f"✓ 获取每日提交次数: {daily_count}")
    
    # 获取学生注册信息
    registered_info = get_student_registered_info(test_student_id)
    if registered_info:
        print(f"✓ 获取学生注册信息: {registered_info['name']}, {registered_info.get('nickname')}")
    else:
        print("⚠️  未找到学生注册信息")


def test_leaderboard():
    """测试排行榜功能"""
    print("\n" + "=" * 80)
    print("测试3: 排行榜功能")
    print("=" * 80)
    
    test_assignment_id = "test_01"
    
    # 创建测试排行榜
    test_leaderboard = [
        {
            "student_info": {
                "student_id": "test_student_001",
                "name": "测试学生1",
                "nickname": "测试1"
            },
            "score": 0.4,
            "metrics": {
                "MAE": 0.4,
                "MSE": 0.2,
                "RMSE": 0.3,
                "Prediction_Time": 0.1
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "submission_count": 1
        },
        {
            "student_info": {
                "student_id": "test_student_002",
                "name": "测试学生2",
                "nickname": "测试2"
            },
            "score": 0.5,
            "metrics": {
                "MAE": 0.5,
                "MSE": 0.3,
                "RMSE": 0.4,
                "Prediction_Time": 0.1
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "submission_count": 1
        }
    ]
    
    # 更新排行榜
    try:
        update_leaderboard(test_assignment_id, test_leaderboard)
        print(f"✓ 更新测试排行榜成功: {test_assignment_id}")
    except Exception as e:
        print(f"❌ 更新测试排行榜失败: {e}")
        return
    
    # 读取排行榜
    leaderboard = get_leaderboard(test_assignment_id)
    print(f"✓ 读取排行榜成功: {len(leaderboard)} 名学生")
    
    for i, entry in enumerate(leaderboard, 1):
        print(f"  {i}. {entry['student_info']['name']} - Score: {entry['score']}")


def test_assignment_ids():
    """测试获取所有作业ID"""
    print("\n" + "=" * 80)
    print("测试4: 获取所有作业ID")
    print("=" * 80)
    
    assignment_ids = get_all_assignment_ids()
    print(f"✓ 找到 {len(assignment_ids)} 个作业:")
    for assignment_id in assignment_ids:
        count = get_submission_count("test_student_001", assignment_id)
        print(f"  - {assignment_id}: {count} 条提交记录")


def test_file_structure():
    """测试文件结构"""
    print("\n" + "=" * 80)
    print("测试5: 验证文件结构")
    print("=" * 80)
    
    from app.services.storage_service import (
        DATABASE_DIR,
        SUBMISSIONS_DIR,
        LEADERBOARD_DIR,
        CHECKPOINT_SUBMISSIONS_DIR,
        CHECKPOINT_LEADERBOARD_DIR
    )
    
    directories = {
        "database": DATABASE_DIR,
        "submissions": SUBMISSIONS_DIR,
        "leaderboard": LEADERBOARD_DIR,
        "checkpoint/submissions": CHECKPOINT_SUBMISSIONS_DIR,
        "checkpoint/leaderboard": CHECKPOINT_LEADERBOARD_DIR
    }
    
    for name, path in directories.items():
        if path.exists():
            print(f"✓ {name}: {path}")
        else:
            print(f"⚠️  {name}: {path} (不存在)")
    
    # 列出submissions文件
    if SUBMISSIONS_DIR.exists():
        submission_files = list(SUBMISSIONS_DIR.glob("submissions_*.json"))
        print(f"\n✓ submissions目录下有 {len(submission_files)} 个文件:")
        for file in submission_files:
            print(f"  - {file.name}")
    
    # 列出leaderboard文件
    if LEADERBOARD_DIR.exists():
        leaderboard_files = list(LEADERBOARD_DIR.glob("leaderboard_*.json"))
        print(f"\n✓ leaderboard目录下有 {len(leaderboard_files)} 个文件:")
        for file in leaderboard_files:
            print(f"  - {file.name}")


def main():
    """运行所有测试"""
    print("\n")
    print("=" * 80)
    print(" 测试新的存储结构")
    print("=" * 80)
    
    try:
        test_basic_storage()
        test_submissions()
        test_leaderboard()
        test_assignment_ids()
        test_file_structure()
        
        print("\n" + "=" * 80)
        print(" ✓ 所有测试完成!")
        print("=" * 80)
        print()
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

