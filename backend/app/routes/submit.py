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
    get_assignment_config
)
from ..services.leaderboard_service import update_student_leaderboard
from ..services.backup_service import check_and_archive_deadline

router = APIRouter(prefix="/api", tags=["submission"])


@router.post("/submit", response_model=SubmissionResponse)
async def submit_assignment(submission: SubmissionRequest):
    """
    提交作业接口
    
    执行流程：
    1. 检查截止时间
    2. 校验提交次数限制
    3. 校验MD5
    4. 保存提交记录（补全timestamp、submission_count）
    5. 更新排行榜（根据提交次数和分数比较）
    6. 返回提交状态信息
    """
    
    # 步骤0: 获取作业配置
    assignment_config = get_assignment_config(submission.assignment_id)
    
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
        
        # 检查evaluate.py的MD5
        if "evaluate.py" in expected_checksums:
            expected_md5 = expected_checksums["evaluate.py"]
            submitted_md5 = submission.checksums.get("evaluate.py", "")
            
            if submitted_md5 != expected_md5:
                raise HTTPException(
                    status_code=400,
                    detail="MD5校验失败"
                )
    
    # 步骤4: 保存当前提交
    # 获取提交次数（当前次数 + 1）
    submission_count = get_submission_count(
        submission.student_info.student_id,
        submission.assignment_id
    ) + 1
    
    # 生成时间戳
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # 构造完整的提交数据
    complete_submission_data = CompleteSubmissionData(
        metrics=submission.metrics,
        timestamp=timestamp,
        submission_count=submission_count
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
    leaderboard_updated, current_rank, score, previous_score = update_student_leaderboard(
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
        if previous_score is not None:
            if score > previous_score:
                message = f"提交成功！成绩提升（{previous_score:.6f} → {score:.6f}），排行榜已更新"
            elif abs(score - previous_score) < 1e-9:
                message = f"提交成功！成绩与之前相同（{score:.6f}），已更新提交时间"
            else:
                message = f"提交成功，成绩未提升（{score:.6f} < {previous_score:.6f}），排行榜不变"
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

