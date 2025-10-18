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
    save_submission
)
from ..services.leaderboard_service import update_student_leaderboard
from ..services.signature_service import generate_signature, verify_client_signature

router = APIRouter(prefix="/api", tags=["submission"])


@router.post("/submit", response_model=SubmissionResponse)
async def submit_assignment(submission: SubmissionRequest):
    """
    提交作业接口
    
    执行流程：
    1. 检查截止时间
    2. 保存提交记录（补全timestamp、submission_count、signature）
    3. 更新排行榜（根据提交次数和分数比较）
    4. 返回提交状态信息
    """
    
    # 步骤1: 检查截止时间
    if is_deadline_passed(submission.assignment_id):
        raise HTTPException(
            status_code=400,
            detail="提交超时：当前时间已超过作业截止时间"
        )
    
    # 步骤1.5: 验证签名（如果提供）
    if submission.signature:
        if not verify_client_signature(
            student_id=submission.student_info.student_id,
            assignment_id=submission.assignment_id,
            metrics=submission.submission_data.metrics.dict(),
            signature=submission.signature
        ):
            raise HTTPException(
                status_code=400,
                detail="签名不规范：签名验证失败"
            )
    
    # 步骤2: 保存当前提交
    # 获取提交次数（当前次数 + 1）
    submission_count = get_submission_count(
        submission.student_info.student_id,
        submission.assignment_id
    ) + 1
    
    # 生成时间戳
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # 构造完整的提交数据
    complete_submission_data = CompleteSubmissionData(
        metrics=submission.submission_data.metrics,
        timestamp=timestamp,
        submission_count=submission_count
    )
    
    # 构造完整提交记录（用于生成签名）
    submission_dict = {
        "student_info": submission.student_info.dict(),
        "assignment_id": submission.assignment_id,
        "submission_data": complete_submission_data.dict()
    }
    
    # 生成签名
    signature = generate_signature(submission_dict)
    
    # 构造完整提交对象
    complete_submission = CompleteSubmission(
        student_info=submission.student_info,
        assignment_id=submission.assignment_id,
        submission_data=complete_submission_data,
        signature=signature
    )
    
    # 保存到提交历史
    save_submission(complete_submission.dict())
    
    # 步骤3: 排名与更新逻辑
    leaderboard_updated, current_rank, score, previous_score = update_student_leaderboard(
        student_info=submission.student_info.dict(),
        assignment_id=submission.assignment_id,
        metrics=submission.submission_data.metrics.dict(),
        timestamp=timestamp,
        submission_count=submission_count
    )
    
    # 步骤4: 返回提交状态信息
    if submission_count == 1:
        message = "首次提交成功，已加入排行榜"
    else:
        if previous_score is not None:
            if score > previous_score:
                message = f"提交成功！成绩提升（{previous_score:.6f} → {score:.6f}），排行榜已更新"
            elif abs(score - previous_score) < 1e-9:
                message = f"提交成功！成绩与之前相同（{score:.6f}），已更新提交时间"
            else:
                message = f"提交成功，但成绩未提升（{score:.6f} < {previous_score:.6f}），排行榜保持不变"
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

