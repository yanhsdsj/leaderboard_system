import sys
import time
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor


def evaluate():
    """
    评测函数，执行并发预测并计算评测指标

    Returns:
        dict: 包含MAE, MSE, RMSE和Prediction_Time
    """
    from solution import Solution

    solution = Solution()

    test_df = pd.read_csv('test.csv')
    y_true = test_df.iloc[:, 1].values  # B列（年龄）

    samples = [(idx, row.to_dict()) for idx, row in test_df.iterrows()]
    predictions = [None] * len(samples)

    def process_sample(sample_info):
        """
        处理单个样本的预测

        Args:
            sample_info: (idx, sample_dict)元组

        Returns:
            tuple: (idx, prediction)
        """
        idx, sample = sample_info
        result = solution.forward(sample)
        return idx, result['prediction']

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process_sample, samples)
        for idx, pred in results:
            predictions[idx] = pred
    prediction_time = time.time() - start_time

    predictions = np.array(predictions)
    mae = np.mean(np.abs(y_true - predictions))
    mse = np.mean((y_true - predictions) ** 2)
    rmse = np.sqrt(mse)

    metrics = {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'Prediction_Time': prediction_time
    }

    return metrics


if __name__ == "__main__":
    results = evaluate()
    for metric, value in results.items():
        if metric == 'Prediction_Time':
            print(f"{metric}: {value:.2f}s")
        else:
            print(f"{metric}: {value:.4f}")