from fastapi import APIRouter, HTTPException
from datetime import datetime
from ..models.submission import (
    SubmissionRequest,
    CompleteSubmission,
    CompleteSubmissionData,
    SubmissionResponse
)
from ..services.storage_service import (
    is_deadline_passed,
    get_submission_count,
    get_daily_submission_count,
    save_submission,
    get_assignment_config,
    get_student_registered_info
)
from ..services.leaderboard_service import update_student_leaderboard
from ..services.backup_service import check_and_archive_deadline

router = APIRouter(prefix="/api", tags=["submission"])


@router.post("/submit", response_model=SubmissionResponse)
async def submit_assignment(submission: SubmissionRequest):
    """
    提交作业接口
    
    执行流程：
    1. 验证作业ID和数据字段
    2. 检查截止时间
    3. 校验提交次数限制
    4. 校验MD5
    5. 保存提交记录（补全timestamp、submission_count）
    6. 更新排行榜（根据提交次数和分数比较）
    7. 返回提交状态信息
    """
    
    # 步骤0: 验证作业ID是否存在
    assignment_config = get_assignment_config(submission.assignment_id)
    if assignment_config is None:
        raise HTTPException(
            status_code=400,
            detail=f"无效的作业ID：{submission.assignment_id}，该作业不存在"
        )
    
    # 步骤0.0: 验证学生信息是否与注册信息一致
    # 检查student_id、name和nickname三者是否都匹配
    registered_info = get_student_registered_info(submission.student_info.student_id)
    if registered_info is not None:
        # 该学生ID已经提交过，需要验证name和nickname是否都一致
        mismatches = []
        
        if registered_info['name'] != submission.student_info.name:
            mismatches.append(f"姓名（已绑定: '{registered_info['name']}'，当前提交: '{submission.student_info.name}'）")
        
        # 比较nickname，需要处理None的情况
        registered_nickname = registered_info.get('nickname')
        submitted_nickname = submission.student_info.nickname
        if registered_nickname != submitted_nickname:
            mismatches.append(f"昵称（已绑定: '{registered_nickname}'，当前提交: '{submitted_nickname}'）")
        
        if mismatches:
            raise HTTPException(
                status_code=403,
                detail=f"身份验证失败：学生ID '{submission.student_info.student_id}' 的信息不匹配。{'; '.join(mismatches)}。学生信息一经绑定不可修改，请使用首次提交时的信息。"
            )
    # 如果是首次提交（registered_info is None），则接受并记录该student_info的所有内容
    
    # 步骤0.1: 验证所有必需的指标字段是否存在（根据assignment配置动态确定）
    # 从assignment配置中获取需要的指标
    required_metrics = list(assignment_config.get("metrics", {}).keys()) if assignment_config else []
    
    # 如果配置中没有metrics，则使用默认的指标
    if not required_metrics:
        required_metrics = ["MAE", "MSE", "RMSE", "Prediction_Time"]
    
    metrics_dict = submission.metrics.dict()
    missing_metrics = []
    invalid_metrics = []
    
    for metric in required_metrics:
        if metric not in metrics_dict or metrics_dict[metric] is None:
            missing_metrics.append(metric)
        else:
            # 验证指标值是否为有效数字（非负数）
            value = metrics_dict[metric]
            if not isinstance(value, (int, float)) or value < 0:
                invalid_metrics.append(f"{metric}={value}")
    
    if missing_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"数据格式错误：缺少必需的指标字段 {', '.join(missing_metrics)}"
        )
    
    if invalid_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"数据格式错误：指标值必须为非负数 {', '.join(invalid_metrics)}"
        )
    
    # 步骤1: 检查截止时间
    if is_deadline_passed(submission.assignment_id):
        # 检查是否需要归档
        if assignment_config and "deadline" in assignment_config:
            check_and_archive_deadline(
                submission.assignment_id,
                assignment_config["deadline"]
            )
        
        raise HTTPException(
            status_code=400,
            detail="提交超时：当前时间已超过作业截止时间"
        )
    
    # 步骤2: 校验每日提交次数限制
    if assignment_config:
        max_submissions = assignment_config.get("max_submissions", 100)
        # 获取今日提交次数
        current_daily_count = get_daily_submission_count(
            submission.student_info.student_id,
            submission.assignment_id
        )
        
        if current_daily_count >= max_submissions:
            raise HTTPException(
                status_code=400,
                detail=f"已达到今日最大提交次数限制（{max_submissions}次/天）"
            )
    
    # 步骤3: 校验MD5
    if assignment_config and "checksums" in assignment_config:
        expected_checksums = assignment_config["checksums"]
        failed_files = []
        
        # 检查所有需要验证的文件
        for filename, expected_md5 in expected_checksums.items():
            submitted_md5 = submission.checksums.get(filename, "")
            
            if submitted_md5 != expected_md5:
                failed_files.append(filename)
        
        if failed_files:
            raise HTTPException(
                status_code=400,
                detail=f"MD5校验失败：{', '.join(failed_files)} 文件的MD5不匹配"
            )
    
    # 步骤4: 保存当前提交
    # 获取提交次数（当前次数 + 1）
    submission_count = get_submission_count(
        submission.student_info.student_id,
        submission.assignment_id
    ) + 1
    
    # 生成时间戳
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # 构造完整的提交数据（包含文件内容和校验和）
    complete_submission_data = CompleteSubmissionData(
        metrics=submission.metrics,
        timestamp=timestamp,
        submission_count=submission_count,
        checksums=submission.checksums,
        files=submission.files
    )
    
    # 构造完整提交对象
    complete_submission = CompleteSubmission(
        student_info=submission.student_info,
        assignment_id=submission.assignment_id,
        submission_data=complete_submission_data
    )
    
    # 保存到提交历史
    save_submission(complete_submission.dict())
    
    # 步骤5: 排名与更新逻辑
    leaderboard_updated, current_rank, score, previous_score, metric_direction = update_student_leaderboard(
        student_info=submission.student_info.dict(),
        assignment_id=submission.assignment_id,
        metrics=submission.metrics.dict(),
        timestamp=timestamp,
        submission_count=submission_count
    )
    
    # 步骤6: 返回提交状态信息
    if submission_count == 1:
        message = "首次提交成功，已加入排行榜"
    else:
        if previous_score is not None and score is not None:
            # 根据指标方向判断是提升还是下降
            if metric_direction == 'max':
                # 越大越好：新分数 > 旧分数 表示提升
                is_better = score > previous_score
            else:
                # 越小越好：新分数 < 旧分数 表示提升
                is_better = score < previous_score
            
            # 检查是否相同
            if abs(score - previous_score) < 1e-9:
                message = f"提交成功！指标与之前相同（{score:.6f}），已更新提交时间"
            elif is_better:
                message = f"提交成功！指标更优（{previous_score:.6f} → {score:.6f}），排行榜已更新"
            else:
                message = f"提交成功，指标未提升（{score:.6f}），排行榜保持最佳成绩（{previous_score:.6f}）"
        elif leaderboard_updated:
            message = "提交成功，排行榜已更新"
        else:
            message = "提交成功"
    
    return SubmissionResponse(
        success=True,
        message=message,
        submission_count=submission_count,
        leaderboard_updated=leaderboard_updated,
        current_rank=current_rank,
        score=score,
        previous_score=previous_score
    )

