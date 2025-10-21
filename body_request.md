请求格式
Headers
Content-Type: application/json
Body
{
  "student_info": {
    "student_id": "2021001234",
    "name": "张三",
    "nickname": "代码小能手"
  },
  "assignment_id": "01",
  "metrics": {
    "MAE": 0.1234,
    "MSE": 0.5678,
    "RMSE": 0.7536,
    "Prediction_Time": 12.34
  },
  "checksums": {
    "evaluate.py": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
  }
}
字段说明：
● student_info: 学生信息（必填）
  ○ student_id: 学生学号（必填）
  ○ name: 学生姓名（必填）
  ○ nickname: 学生昵称（必填）
● assignment_id: 作业编号（必填）
● metrics: 评估指标（必填）
  ○ MAE: 平均绝对误差
  ○ MSE: 均方误差
  ○ RMSE: 均方根误差（排序依据）
  ○ Prediction_Time: 预测时间（秒）
● checksums: 文件MD5校验和（必填）
  ○ evaluate.py: evaluate.py文件的MD5值
test.csv 的校验当前不需要。

响应格式
1. 成功 - 200 OK
{
  "rank": 5,
  "message": "提交成功"
}
2. MD5校验失败 - 400 Bad Request
{
  "error": "Checksum mismatch",
  "details": "evaluate.py 文件已被修改"
}
3. 截止时间超时 - 400 Bad Request
{
  "error": "Deadline passed",
  "details": "提交超时：当前时间已超过作业截止时间"
}
4. 学号无效 - 401 Unauthorized
{
  "error": "Invalid student_id",
  "details": "学号不能为空"
}
5. 提交次数超限 - 400 Bad Request
{
  "error": "Submission limit exceeded",
  "details": "已达到最大提交次数限制（100次）"
}
6. 数据格式错误 - 422 Unprocessable Entity
只选择了会在leaderboad上进行排序的字段
{
  "detail": [
    {
      "loc": ["body", "metrics", "RMSE"],
      "msg": "field required: 预测指标 RMSE为必填项，不可缺失",
      "type": "value_error.missing.metrics",
      "ctx": {
        "required_field": "RMSE",
        "field_desc": "RMSE"
      }
    },
    {
      "loc": ["body", "metrics", "Prediction_Time"],
      "msg": "field required: 预测指标 Prediction_Time（预测耗时）为必填项，不可缺失",
      "type": "value_error.missing.metrics",
      "ctx": {
        "required_field": "Prediction_Time",
        "field_desc": "预测耗时"
      }
    }
  ],
  "code": 422,
  "message": "请求数据验证失败：metrics 指标存在 2 个缺失字段，请补充完整"
}

