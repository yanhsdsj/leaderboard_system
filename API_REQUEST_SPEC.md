# 排行榜系统 API 请求规范

## 📌 提交作业接口

### 基本信息
- **URL**: `/api/submit`
- **Method**: `POST`
- **Content-Type**: `application/json`

---

## 📤 请求体 (Request Body)

### 完整示例
```json
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
```

### 字段说明

#### 1. `student_info` (对象，必填)
学生信息对象

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `student_id` | string | ✅ 是 | 学生学号，唯一标识 | "2021001234" |
| `name` | string | ✅ 是 | 学生姓名 | "张三" |
| `nickname` | string | ❌ 否 | 学生昵称（可选） | "代码小能手" |

#### 2. `assignment_id` (字符串，必填)
作业编号

- **类型**: string
- **必填**: ✅ 是
- **说明**: 作业的唯一标识符，必须在系统中存在
- **示例**: `"01"`, `"02"`, `"03"`

#### 3. `metrics` (对象，必填)
评估指标对象，所有字段均为必填

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `MAE` | float | ✅ 是 | 平均绝对误差 | 0.1234 |
| `MSE` | float | ✅ 是 | 均方误差 | 0.5678 |
| `RMSE` | float | ✅ 是 | 均方根误差（主排序指标） | 0.7536 |
| `Prediction_Time` | float | ✅ 是 | 推理时间（秒，次排序指标） | 12.34 |

**排序规则**：
1. 优先按 `RMSE` 升序（越小越好）
2. RMSE相同时按 `Prediction_Time` 升序（越小越好）
3. 都相同时按提交时间升序（越早越好）

#### 4. `checksums` (对象，必填)
文件MD5校验和

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `evaluate.py` | string | ✅ 是 | evaluate.py文件的MD5值，必须匹配预设值 |

**当前预设MD5值** (作业01): `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

---

## 📥 响应体 (Response)

### 1. 成功 - 200 OK

```json
{
  "success": true,
  "message": "提交成功！成绩提升（0.8536 → 0.7536），排行榜已更新",
  "submission_count": 3,
  "leaderboard_updated": true,
  "current_rank": 5,
  "score": 0.7536,
  "previous_score": 0.8536
}
```

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 是否成功 |
| `message` | string | 详细消息 |
| `submission_count` | integer | 当前提交次数 |
| `leaderboard_updated` | boolean | 排行榜是否更新 |
| `current_rank` | integer/null | 当前排名 |
| `score` | float/null | 当前分数（RMSE值） |
| `previous_score` | float/null | 之前的分数 |

#### 可能的成功消息

- `"首次提交成功，已加入排行榜"` - 第一次提交
- `"提交成功！成绩提升（0.8536 → 0.7536），排行榜已更新"` - 成绩提升
- `"提交成功！成绩与之前相同（0.7536），已更新提交时间"` - 成绩相同
- `"提交成功，成绩未提升（0.8536 < 0.7536），排行榜不变"` - 成绩未提升
- `"提交成功"` - 其他情况

---

### 2. 截止时间超时 - 400 Bad Request

```json
{
  "detail": "提交超时：当前时间已超过作业截止时间"
}
```

**发生条件**: 当前时间超过作业截止时间

---

### 3. 提交次数超限 - 400 Bad Request

```json
{
  "detail": "已达到最大提交次数限制（10次）"
}
```

**发生条件**: 已提交次数 ≥ 最大允许次数（默认10次）

---

### 4. MD5校验失败 - 400 Bad Request

```json
{
  "detail": "MD5校验失败"
}
```

**发生条件**: 提交的evaluate.py的MD5值与预设值不匹配

---

### 5. 数据格式错误 - 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "student_info", "student_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**发生条件**: 
- 缺少必填字段
- 字段类型错误
- 数据格式不符合要求

---

## 🧪 测试示例

### Python 示例

```python
import requests
import hashlib

# 计算文件MD5
def compute_file_md5(filepath):
    md5_hash = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

# 提交数据
url = "http://localhost:8000/api/submit"
data = {
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
        "evaluate.py": compute_file_md5("evaluate.py")
    }
}

response = requests.post(url, json=data)
print(response.json())
```

### cURL 示例

```bash
curl -X POST "http://localhost:8000/api/submit" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

---

## ⚙️ 系统配置

### 作业配置 (assignments.json)

```json
{
  "01": {
    "assignment_id": "01",
    "title": "作业1",
    "deadline": "2025-12-31T23:59:59Z",
    "checksums": {
      "evaluate.py": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
    },
    "max_submissions": 100
  }
}
```

### 关键配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `deadline` | 截止时间（UTC时间） | - |
| `max_submissions` | 最大提交次数 | 10 |
| `checksums.evaluate.py` | evaluate.py的MD5预设值 | - |

---

## 📝 注意事项

1. **时区**: 所有时间戳使用UTC时区，格式为ISO 8601
2. **MD5校验**: 必须提交正确的evaluate.py的MD5值
3. **提交限制**: 默认最多提交10次（可在配置中修改）
4. **排序逻辑**: RMSE → Prediction_Time → 提交时间（均升序）
5. **排行榜更新**: 仅当新分数优于旧分数时才更新排行榜
6. **nickname可选**: 如不需要可设为null或省略

---

## 🔍 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `field required` | 缺少必填字段 | 检查所有必填字段是否提供 |
| `MD5校验失败` | MD5值不匹配 | 使用正确的evaluate.py文件 |
| `提交超时` | 超过截止时间 | 在截止时间前提交 |
| `提交次数超限` | 达到最大次数 | 无法继续提交 |
| `value is not a valid float` | 数值类型错误 | 确保metrics中所有值为数字 |

---

**生成时间**: 2025-10-21  
**版本**: v1.0  
**后端框架**: FastAPI + Pydantic

