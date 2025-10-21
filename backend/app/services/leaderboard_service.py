from typing import Dict, List, Optional, Tuple
from .storage_service import (
    get_assignment_config,
    get_leaderboard,
    update_leaderboard,
    get_student_leaderboard_entry
)


def calculate_score(metrics: Dict, weights: Dict = None) -> float:
    """
    根据指标计算综合得分，可自行定义
    
    对于"越小越好"的指标，使用 1/(1+value) 进行归一化
    
    Args:
        metrics: 指标字典
        weights: 权重字典
        
    Returns:
        综合得分（越大越好）
    """
    if weights is None:
        # 默认权重
        weights = {
            "MAE": 0.25,
            "MSE": 0.25,
            "RMSE": 0.25,
            "Prediction_Time": 0.25
        }
    
    # 所有指标都是越小越好，使用归一化
    # score = (
    #     weights.get("MAE", 0.25) * (1 / (1 + metrics["MAE"])) +
    #     weights.get("MSE", 0.25) * (1 / (1 + metrics["MSE"])) +
    #     weights.get("RMSE", 0.25) * (1 / (1 + metrics["RMSE"])) +
    #     weights.get("Prediction_Time", 0.25) * (1 / (1 + metrics["Prediction_Time"]))
    # )
    score = metrics["RMSE"]
    return round(score, 4)



def compare_scores(new_score: float, old_score: float) -> int:
    """
    比较两个分数
    
    Args:
        new_score: 新分数
        old_score: 旧分数
        
    Returns:
        1: 新分数更优, 0: 分数相同, -1: 旧分数更优
    """
    if abs(new_score - old_score) < 1e-9:  # 处理浮点数精度问题
        return 0
    elif new_score < old_score:
        return 1
    else:
        return -1


def update_student_leaderboard(
    student_info: Dict,
    assignment_id: str,
    metrics: Dict,
    timestamp: str,
    submission_count: int
) -> Tuple[bool, Optional[int], float, Optional[float]]:
    """
    更新学生在排行榜中的记录
    
    Args:
        student_info: 学生信息
        assignment_id: 作业ID
        metrics: 评估指标
        timestamp: 提交时间戳
        submission_count: 提交次数
        
    Returns:
        (是否更新了排行榜, 当前排名, 当前分数, 之前的分数)
    """
    # 获取作业配置
    config = get_assignment_config(assignment_id)
    weights = config.get("weights") if config else None
    
    # 计算新分数
    new_score = calculate_score(metrics, weights)
    
    # 获取当前排行榜
    leaderboard = get_leaderboard(assignment_id)
    
    # 查找学生现有记录
    existing_entry = None
    existing_index = -1
    for idx, entry in enumerate(leaderboard):
        if entry['student_info']['student_id'] == student_info['student_id']:
            existing_entry = entry
            existing_index = idx
            break
    
    leaderboard_updated = False
    previous_score = None
    
    if submission_count == 1:
        # 首次提交，直接加入排行榜
        new_entry = {
            "student_info": student_info,
            "score": new_score,
            "metrics": metrics,
            "timestamp": timestamp,
            "submission_count": submission_count
        }
        leaderboard.append(new_entry)
        leaderboard_updated = True
    else:
        # 非首次提交，需要比较分数
        if existing_entry:
            old_score = existing_entry['score']
            previous_score = old_score
            comparison = compare_scores(new_score, old_score)
            
            if comparison > 0:
                # 新分数更优，更新排行榜
                leaderboard[existing_index] = {
                    "student_info": student_info,
                    "score": new_score,
                    "metrics": metrics,
                    "timestamp": timestamp,
                    "submission_count": submission_count
                }
                leaderboard_updated = True
            elif comparison == 0:
                # 分数相同，只更新时间戳和提交次数
                leaderboard[existing_index]['timestamp'] = timestamp
                leaderboard[existing_index]['submission_count'] = submission_count
                leaderboard_updated = True  # 虽然分数未变，但记录已更新
            # else: 新分数较差，不更新
    
    # 按分数排序（升序，因为RMSE越小越好）
    leaderboard.sort(key=lambda x: x['score'], reverse=False)
    
    # 保存更新后的排行榜
    update_leaderboard(assignment_id, leaderboard)
    
    # 查找当前排名
    current_rank = None
    for idx, entry in enumerate(leaderboard):
        if entry['student_info']['student_id'] == student_info['student_id']:
            current_rank = idx + 1
            break
    
    return leaderboard_updated, current_rank, new_score, previous_score


def get_ranked_leaderboard(assignment_id: str) -> List[Dict]:
    """
    获取带排名的排行榜
    
    Args:
        assignment_id: 作业ID
        
    Returns:
        排行榜列表（每条记录包含rank字段）
    """
    leaderboard = get_leaderboard(assignment_id)
    
    # 添加排名
    ranked_leaderboard = []
    for idx, entry in enumerate(leaderboard):
        ranked_entry = entry.copy()
        ranked_entry['rank'] = idx + 1
        ranked_leaderboard.append(ranked_entry)
    
    return ranked_leaderboard

