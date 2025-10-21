import sys
import time
import os
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import hashlib
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# ==================== 配置区 ====================
LEADERBOARD_URL = "http://your-server.com/api/submit"
STUDENT_ID_FILE = os.path.join(current_dir, '.student_id')


# ================================================


def compute_file_md5(filepath):
    """计算文件的MD5哈希值"""
    md5_hash = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except FileNotFoundError:
        return None


def get_student_id():
    """获取学号，首次运行需要输入，之后自动读取"""
    # 尝试从文件读取
    if os.path.exists(STUDENT_ID_FILE):
        try:
            with open(STUDENT_ID_FILE, 'r', encoding='utf-8') as f:
                student_id = f.read().strip()
                if student_id:
                    print(f"✓ 使用已保存的学号: {student_id}")
                    return student_id
        except:
            pass

    # 首次运行，提示输入
    print("\n" + "=" * 50)
    print("首次运行，请输入你的学号")
    print("=" * 50)

    import termios
    try:
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except:
        pass

    while True:
        student_id = input("请输入学号: ").strip()
        if student_id:
            try:
                with open(STUDENT_ID_FILE, 'w', encoding='utf-8') as f:
                    f.write(student_id)
                print(f"✓ 学号已保存，下次运行无需输入")
            except Exception as e:
                print(f"⚠️  警告：学号保存失败 ({e})，下次需要重新输入")
            return student_id
        else:
            print("学号不能为空，请重新输入！")


if __name__ == "__main__":
    # 获取学号
    student_id = get_student_id()

    # ==================== 合规性检查 ====================
    print("\n验证模型合规性...")

    # 检查禁止的机器学习库（运行时检查）
    forbidden = ['sklearn', 'scikit_learn', 'tensorflow', 'torch', 'pytorch',
                 'keras', 'xgboost', 'lightgbm', 'catboost', 'statsmodels']

    imported = list(sys.modules.keys())
    violations = []
    for module in imported:
        module_lower = module.lower()
        for pkg in forbidden:
            if module_lower == pkg or module_lower.startswith(pkg + '.'):
                violations.append(module)
                break

    if violations:
        print("❌ 检测到禁止的库:", violations)
        sys.exit(1)

    print("✓ 合规性检查通过")
    # ====================================================

    # 检查训练好的模型
    model_params_path = os.path.join(parent_dir, 'model_params.pkl')
    if not os.path.exists(model_params_path):
        print("警告: 未找到模型参数文件", file=sys.stderr)
        print("正在尝试训练模型...", file=sys.stderr)
        try:
            os.chdir(parent_dir)
            import train

            print("模型训练完成", file=sys.stderr)
        except Exception as e:
            print(f"错误: 训练失败 - {str(e)}", file=sys.stderr)
            sys.exit(1)
        finally:
            os.chdir(current_dir)

    # 加载模型
    os.chdir(parent_dir)
    from solution import Solution

    solution = Solution()
    os.chdir(current_dir)

    # 读取测试数据
    test_df = pd.read_csv('test.csv')
    original_size = len(test_df)
    np.random.seed(42)
    sample_indices = np.random.choice(original_size, 10000, replace=False)
    test_df = test_df.iloc[sample_indices].reset_index(drop=True)
    y_true = test_df['age'].values

    test_features = test_df.drop('age', axis=1)
    samples = [(idx, row.to_dict()) for idx, row in test_features.iterrows()]
    predictions = [None] * len(samples)


    def process_sample(sample_info):
        idx, sample = sample_info
        result = solution.forward(sample)
        return idx, result['prediction']


    print("开始预测...")
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process_sample, samples)
        for idx, pred in results:
            predictions[idx] = pred
    prediction_time = time.time() - start_time

    # 计算指标
    predictions = np.array(predictions)
    mae = np.mean(np.abs(y_true - predictions))
    mse = np.mean((y_true - predictions) ** 2)
    rmse = np.sqrt(mse)

    # 显示结果
    print("\n" + "=" * 50)
    print("评测结果:")
    print("=" * 50)
    print(f"MAE: {mae:.4f}")
    print(f"MSE: {mse:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"Prediction_Time: {prediction_time:.2f}s")
    print("=" * 50)

    # 计算文件MD5并提交到leaderboard
    checksums = {
        'evaluate.py': compute_file_md5(os.path.join(current_dir, 'evaluate.py')),
        'test.csv': compute_file_md5(os.path.join(current_dir, 'test.csv')),
    }

    payload = {
        'student_id': student_id,
        'metrics': {
            'MAE': mae,
            'MSE': mse,
            'RMSE': rmse,
            'Prediction_Time': prediction_time
        },
        'checksums': checksums,
    }

    try:
        print("\n正在提交到leaderboard...")
        response = requests.post(
            LEADERBOARD_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ 提交成功!")
            if 'rank' in result:
                print(f"🏆 当前排名: {result['rank']}")
            if 'message' in result:
                print(f"📝 {result['message']}")
        else:
            print(f"❌ 提交失败: {response.text}")

    except Exception as e:
        print(f"❌ 提交错误: {str(e)}")