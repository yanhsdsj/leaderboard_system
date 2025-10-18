# Leaderboard System

学生作业提交与排行榜管理系统

## 项目结构

```
leaderboard_system/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── main.py            # FastAPI应用入口
│   │   ├── models/            # 数据模型
│   │   │   ├── student.py     # 学生信息模型
│   │   │   └── submission.py  # 提交和排行榜模型
│   │   ├── routes/            # API路由
│   │   │   ├── health.py      # 健康检查
│   │   │   ├── submit.py      # 提交作业
│   │   │   └── leaderboard.py # 排行榜查询
│   │   ├── services/          # 业务逻辑
│   │   │   ├── storage_service.py     # 数据存储
│   │   │   ├── leaderboard_service.py # 排行榜管理
│   │   │   └── signature_service.py   # 签名验证
│   │   └── utils/             # 工具函数
│   ├── database/              # JSON数据库
│   │   ├── submissions.json   # 提交历史
│   │   ├── leaderboard.json   # 排行榜数据
│   │   └── assignments.json   # 作业配置
│   └── requirements.txt       # Python依赖
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── App.jsx           # 主应用组件
│   │   ├── main.jsx          # 应用入口
│   │   ├── api/
│   │   │   └── api.js        # API调用封装
│   │   └── components/
│   │       ├── LeaderboardTable.jsx    # 排行榜表格
│   │       └── SubmissionDetails.jsx   # 提交详情
│   ├── package.json          # Node依赖
│   └── vite.config.js        # Vite配置
└── example/                  # 测试示例
    └── test_comprehensive.py # 综合测试脚本
```

## 如何运行

### 环境要求

- Python 3.10.18
- Node.js 20.11.0

### 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 方式1：使用start.bat
start.bat

# 方式2：直接运行
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务运行在 http://localhost:8000

API文档: http://localhost:8000/docs

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 方式1：使用start.bat
start.bat

# 方式2：直接运行
npm run dev
```

前端应用运行在 http://localhost:3000

### 测试

```bash
# 运行综合测试脚本
cd example
python test_comprehensive.py
```

```bash
# 运行error测试脚本
cd example
python test_error_handling.py
```

## 主要功能

### 后端API

#### 1. 提交作业
**路由**: `POST /api/submit`

**功能**: 学生提交作业并自动更新排行榜

**请求体**:
```json
{
  "student_info": {
    "student_id": "2021001",
    "name": "张三"
  },
  "assignment_id": "01",
  "submission_data": {
    "metrics": {
      "MAE": 0.5,
      "MSE": 0.3,
      "RMSE": 0.55,
      "Prediction_Time": 0.02
    }
  }
}
```

**响应**:
```json
{
  "success": true,
  "message": "提交成功",
  "submission_count": 1,
  "leaderboard_updated": true,
  "current_rank": 5,
  "score": 0.55,
  "previous_score": null
}
```

#### 2. 获取排行榜
**路由**: `GET /api/leaderboard/{assignment_id}`

**功能**: 获取指定作业的排行榜

**响应**: 按分数排序的学生列表

#### 3. 获取提交历史
**路由**: `GET /api/submissions/{student_id}/{assignment_id}`

**功能**: 查询学生在指定作业的所有提交记录

#### 4. 获取所有作业
**路由**: `GET /api/assignments`

**功能**: 获取所有作业配置（包括截止时间和评分权重）

### 核心函数

#### storage_service.py

- `ensure_database_exists()` - 初始化数据库文件
- `get_assignment_config(assignment_id)` - 获取作业配置
- `is_deadline_passed(assignment_id)` - 检查是否超过截止时间
- `get_submission_count(student_id, assignment_id)` - 获取提交次数
- `save_submission(submission)` - 保存提交记录
- `get_leaderboard(assignment_id)` - 获取排行榜
- `update_leaderboard(assignment_id, leaderboard)` - 更新排行榜

#### leaderboard_service.py

- `calculate_score(metrics, weights)` - 根据指标计算综合得分（当前使用RMSE作为分数）
- `compare_scores(new_score, old_score)` - 比较两个分数（越小越好）
- `update_student_leaderboard(...)` - 更新学生排行榜记录
  - 首次提交：直接加入排行榜
  - 再次提交：仅当分数更优时更新
  - 返回：(是否更新, 当前排名, 当前分数, 之前分数)
- `get_ranked_leaderboard(assignment_id)` - 获取带排名的排行榜

#### signature_service.py

- `generate_signature(data, secret)` - 生成HMAC-SHA256签名
- `verify_signature(data, signature, secret)` - 验证签名有效性

### 前端组件

- `App.jsx` - 主应用，管理排行榜显示和提交详情弹窗
- `LeaderboardTable.jsx` - 排行榜表格，支持点击查看学生提交历史
- `SubmissionDetails.jsx` - 提交详情弹窗，显示学生所有提交记录
- `api.js` - 封装所有API调用（提交、查询排行榜、查询提交历史）

## 评分规则

当前评分逻辑：使用 RMSE 作为分数，越小越好

排行榜更新规则：
- 首次提交：直接加入排行榜
- 再次提交：仅当新分数 < 旧分数时更新（RMSE越小越好）
- 分数相同：更新时间戳和提交次数

可在 `leaderboard_service.py` 的 `calculate_score()` 函数中修改评分逻辑

## 数据存储

使用JSON文件存储数据：

- `database/submissions.json` - 所有提交记录
- `database/leaderboard.json` - 各作业的排行榜
- `database/assignments.json` - 作业配置（截止时间、评分权重）

## 错误处理

系统实现了三种错误处理机制：

### 1. 提交超时
当提交时间超过作业截止时间时返回：
```json
{
  "detail": "提交超时：当前时间已超过作业截止时间"
}
```

### 2. 签名不规范
当客户端提供的签名验证失败时返回：
```json
{
  "detail": "签名不规范：签名验证失败"
}
```

客户端签名生成方法（Python示例）：
```python
import hmac
import hashlib

def generate_client_signature(student_id, assignment_id, metrics):
    msg = (
        f"{student_id}:"
        f"{assignment_id}:"
        f"{metrics['MAE']}:"
        f"{metrics['MSE']}:"
        f"{metrics['RMSE']}:"
        f"{metrics['Prediction_Time']}"
    )
    secret = "ZeroGen-Leaderboard-Secret"
    return hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
```

### 3. 其他错误
系统未预期的错误会返回：
```json
{
  "success": false,
  "message": "其他错误",
  "detail": "具体错误信息"
}
```

## 注意事项

1. 截止时间检查：提交时会检查 `assignments.json` 中配置的截止时间
2. 签名机制：客户端可选提供签名，服务端会验证；所有提交都会生成服务端签名
3. 提交次数统计：自动记录每个学生的提交次数
4. 排行榜排序：按分数升序排列（RMSE越小排名越高）

