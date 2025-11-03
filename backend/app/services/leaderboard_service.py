from typing import Dict, List, Optional, Tuple
from .storage_service import (
    get_assignment_config,
    get_leaderboard,
    update_leaderboard,
    get_student_leaderboard_entry
)


def get_primary_metric_info(metric_priorities: Dict) -> Optional[Tuple[str, str]]:
    """
    获取第一优先级的指标名称和方向
    
    Args:
        metric_priorities: 指标优先级配置字典
                          旧格式: {metric_name: priority}
                          新格式: {metric_name: {"priority": priority, "direction": "min/max"}}
        
    Returns:
        (指标名称, direction) 元组，如果没有则返回 None
    """
    if not metric_priorities:
        return None
    
    # 解析metrics配置（支持新旧两种格式）
    parsed_metrics = []
    for metric_name, config in metric_priorities.items():
        if isinstance(config, dict):
            # 新格式
            priority = config.get('priority', 0)
            direction = config.get('direction', 'min')
        else:
            # 旧格式（兼容）
            priority = config
            direction = 'min'
        
        if priority > 0:
            parsed_metrics.append((metric_name, priority, direction))
    
    if not parsed_metrics:
        return None
    
    # 找出优先级最小（最重要）的指标
    sorted_metrics = sorted(parsed_metrics, key=lambda x: x[1])
    return (sorted_metrics[0][0], sorted_metrics[0][2]) if sorted_metrics else None


def get_primary_metric_name(metric_priorities: Dict) -> Optional[str]:
    """
    获取第一优先级的指标名称（向后兼容）
    
    Args:
        metric_priorities: 指标优先级配置字典
        
    Returns:
        第一优先级的指标名称，如果没有则返回 None
    """
    result = get_primary_metric_info(metric_priorities)
    return result[0] if result else None


def compare_metrics_by_priority(
    metrics_a: Dict,
    metrics_b: Dict,
    metric_priorities: Dict
) -> int:
    """
    根据优先级配置比较两组指标
    
    Args:
        metrics_a: 第一组指标
        metrics_b: 第二组指标
        metric_priorities: 指标优先级配置
                          旧格式: {metric_name: priority}
                          新格式: {metric_name: {"priority": priority, "direction": "min/max"}}
                          
                          priority: 0 表示不参与排序，数字越小优先级越高
                          direction: "min"表示越小越好，"max"表示越大越好
    
    Returns:
        -1: metrics_a 更优
         0: 两组指标相同
         1: metrics_b 更优
    """
    if not metric_priorities:
        # 如果没有配置，默认比较 RMSE（越小越好）
        rmse_a = metrics_a.get("RMSE", float('inf'))
        rmse_b = metrics_b.get("RMSE", float('inf'))
        if rmse_a < rmse_b:
            return -1
        elif rmse_a > rmse_b:
            return 1
        return 0
    
    # 解析metrics配置（支持新旧两种格式）
    parsed_metrics = []
    for metric_name, config in metric_priorities.items():
        if isinstance(config, dict):
            # 新格式
            priority = config.get('priority', 0)
            direction = config.get('direction', 'min')  # 默认越小越好
        else:
            # 旧格式（兼容）
            priority = config
            direction = 'min'  # 旧格式默认越小越好
        
        if priority > 0:
            parsed_metrics.append((metric_name, priority, direction))
    
    # 按优先级排序
    sorted_metrics = sorted(parsed_metrics, key=lambda x: x[1])
    
    # 依次比较每个优先级的指标
    for metric_name, _, direction in sorted_metrics:
        value_a = metrics_a.get(metric_name, float('inf'))
        value_b = metrics_b.get(metric_name, float('inf'))
        
        # 处理浮点数精度问题
        if abs(value_a - value_b) < 1e-9:
            continue  # 相同，比较下一个优先级
        
        # 根据direction判断比较方向
        if direction == 'max':
            # 越大越好
            if value_a > value_b:
                return -1  # metrics_a 更优
            else:
                return 1   # metrics_b 更优
        else:  # direction == 'min' 或其他值默认为min
            # 越小越好
            if value_a < value_b:
                return -1  # metrics_a 更优
            else:
                return 1   # metrics_b 更优
    
    return 0  # 所有指标都相同


def update_student_leaderboard(
    student_info: Dict,
    assignment_id: str,
    metrics: Dict,
    timestamp: str,
    submission_count: int,
    main_contributor: str = None
) -> Tuple[bool, Optional[int], Optional[float], Optional[float], Optional[str]]:
    """
    更新学生在排行榜中的记录
    
    Args:
        student_info: 学生信息
        assignment_id: 作业ID
        metrics: 评估指标
        timestamp: 提交时间戳
        submission_count: 提交次数
        main_contributor: 主要贡献者（human 或 ai）
        
    Returns:
        (是否更新了排行榜, 当前排名, 当前主要指标值, 之前的主要指标值, 指标方向)
    """
    # 获取作业配置
    config = get_assignment_config(assignment_id)
    metric_priorities = config.get("metrics") if config else None
    
    # 获取第一优先级的指标名称和方向
    primary_metric_info = get_primary_metric_info(metric_priorities)
    if primary_metric_info:
        primary_metric_name, metric_direction = primary_metric_info
        new_score = metrics.get(primary_metric_name)
    else:
        primary_metric_name = None
        new_score = None
        metric_direction = 'min'
    
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
            "score": new_score,  # 保存第一优先级的指标值作为 score
            "metrics": metrics,
            "timestamp": timestamp,
            "submission_count": submission_count,
            "main_contributor": main_contributor  # 保存主要贡献者
        }
        leaderboard.append(new_entry)
        leaderboard_updated = True
    else:
        # 非首次提交，需要比较指标
        if existing_entry:
            old_metrics = existing_entry.get('metrics', {})
            old_score = existing_entry.get('score')
            previous_score = old_score
            
            # 使用优先级比较函数
            comparison = compare_metrics_by_priority(metrics, old_metrics, metric_priorities)
            
            if comparison < 0:
                # 新指标更优，更新排行榜（student_info不更新，已绑定不可修改）
                leaderboard[existing_index]['score'] = new_score
                leaderboard[existing_index]['metrics'] = metrics
                leaderboard[existing_index]['timestamp'] = timestamp
                leaderboard[existing_index]['submission_count'] = submission_count
                leaderboard[existing_index]['main_contributor'] = main_contributor  # 更新主要贡献者
                leaderboard_updated = True
            elif comparison == 0:
                # 指标相同，只更新时间戳和提交次数
                leaderboard[existing_index]['timestamp'] = timestamp
                leaderboard[existing_index]['submission_count'] = submission_count
                leaderboard[existing_index]['main_contributor'] = main_contributor  # 更新主要贡献者
                leaderboard_updated = True  # 虽然指标未变，但记录已更新
            else:
                # 新指标较差，只更新提交次数和时间戳
                leaderboard[existing_index]['submission_count'] = submission_count
                leaderboard[existing_index]['timestamp'] = timestamp  # 更新为最后提交时间
                # 注意：不更新分数、指标、main_contributor和student_info，保持最佳成绩
    
    # 使用优先级配置进行排序
    # 使用 functools.cmp_to_key 将比较函数转换为排序键
    from functools import cmp_to_key
    
    def compare_entries(entry_a, entry_b):
        """比较两个排行榜条目"""
        return compare_metrics_by_priority(
            entry_a.get('metrics', {}),
            entry_b.get('metrics', {}),
            metric_priorities
        )
    
    leaderboard.sort(key=cmp_to_key(compare_entries))
    
    # 保存更新后的排行榜
    update_leaderboard(assignment_id, leaderboard)
    
    # 查找当前排名
    current_rank = None
    for idx, entry in enumerate(leaderboard):
        if entry['student_info']['student_id'] == student_info['student_id']:
            current_rank = idx + 1
            break
    
    return leaderboard_updated, current_rank, new_score, previous_score, metric_direction


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



