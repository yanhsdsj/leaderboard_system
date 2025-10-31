import React, { useState, useEffect } from 'react';
import { getStudentSubmissions } from '../api/api';
import './SubmissionDetails.css';

const SubmissionDetails = ({ studentId, assignmentId, assignmentConfig, onClose }) => {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 自动刷新（固定开启，5秒间隔）
  const refreshInterval = 5; // 固定5秒
  const [lastUpdate, setLastUpdate] = useState(null);

  // 获取提交记录的函数（提取出来以便复用）
  const fetchSubmissions = async (showLoading = true) => {
    if (!studentId || !assignmentId) return;
    
    if (showLoading) setLoading(true);
    setError(null);
    try {
      const data = await getStudentSubmissions(studentId, assignmentId);
      setSubmissions(data);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch student submissions:', err);
      setError('无法加载提交记录');
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubmissions();
  }, [studentId, assignmentId]);

  // 自动刷新定时器（固定每5秒）
  useEffect(() => {
    if (!studentId || !assignmentId) return;

    const timer = setInterval(() => {
      fetchSubmissions(false); // 后台刷新，不显示loading
    }, refreshInterval * 1000);

    return () => clearInterval(timer);
  }, [studentId, assignmentId]);

  // 格式化时间戳
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // 格式化上次更新时间
  const formatLastUpdate = () => {
    if (!lastUpdate) return '';
    return lastUpdate.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // 找到最佳提交的索引（不改变顺序）
  const findBestSubmissionIndex = (submissions) => {
    if (!submissions || submissions.length === 0) return -1;
    
    let bestIndex = 0;
    
    for (let i = 1; i < submissions.length; i++) {
      const current = submissions[i].submission_data.metrics;
      const best = submissions[bestIndex].submission_data.metrics;
      
      // 比较 RMSE，如果相同则比较推理时间
      if (current.RMSE < best.RMSE || 
          (current.RMSE === best.RMSE && current.Prediction_Time < best.Prediction_Time)) {
        bestIndex = i;
      }
    }
    
    return bestIndex;
  };

  if (!studentId) {
    return (
      <div className="submission-details-container">
        <div className="empty-state">
          <p>请点击左侧学号查看提交详情</p>
        </div>
      </div>
    );
  }

  return (
    <div className="submission-details-container">
      <div className="details-header">
        <div>
          <h2 className="details-title">提交详情</h2>
          <p className="student-info">学号: {studentId}</p>
        </div>
        <button className="close-button" onClick={onClose}>
          ✕
        </button>
      </div>

      {lastUpdate && (
        <div className="details-controls">
          <div className="last-update">
            自动刷新中 · 最后更新: {formatLastUpdate()}
          </div>
        </div>
      )}

      <div className="submissions-list">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : submissions.length === 0 ? (
          <div className="empty-message">暂无提交记录</div>
        ) : (
          (() => {
            const bestIndex = findBestSubmissionIndex(submissions);
            return submissions.map((submission, index) => (
              <div key={index} className={`submission-card ${index === bestIndex ? 'best-submission' : ''}`}>
                <div className="submission-header">
                  <span className="submission-number">
                    第 {submission.submission_data.submission_count} 次提交
                    {index === bestIndex && <span className="best-badge">最佳</span>}
                  </span>
                  <span className="submission-time">
                    {formatTimestamp(submission.submission_data.timestamp)}
                  </span>
                </div>

              <div className="metrics-grid">
                {/* 动态生成指标显示 - 根据assignment配置的metrics */}
                {assignmentConfig && assignmentConfig.metrics ? (
                  Object.entries(assignmentConfig.metrics)
                    .sort((a, b) => {
                      // 优先显示优先级大于0的指标，按优先级排序
                      const [_, priorityA] = a;
                      const [__, priorityB] = b;
                      if (priorityA === 0 && priorityB === 0) return 0;
                      if (priorityA === 0) return 1;
                      if (priorityB === 0) return -1;
                      return priorityA - priorityB;
                    })
                    .map(([metricName, priority]) => {
                      const value = submission.submission_data.metrics[metricName];
                      const isImportant = priority > 0 && priority <= 2;  // 优先级1,2标记为重要
                      
                      return (
                        <div key={metricName} className="metric-item">
                          <span className={`metric-label ${isImportant ? 'important-metric' : ''}`}>
                            {isImportant ? <strong>{metricName}</strong> : metricName}
                          </span>
                          <span className="metric-value">
                            {typeof value === 'number' ? (
                              metricName === 'Prediction_Time' || metricName.includes('Time') ? 
                                `${value.toFixed(6)}s` : 
                                value.toFixed(6)
                            ) : (value || '-')}
                          </span>
                        </div>
                      );
                    })
                ) : (
                  // 默认显示（兼容旧版本）
                  <>
                    <div className="metric-item">
                      <span className="metric-label">MAE</span>
                      <span className="metric-value">
                        {submission.submission_data.metrics.MAE ? submission.submission_data.metrics.MAE.toFixed(6) : '-'}
                      </span>
                    </div>

                    <div className="metric-item">
                      <span className="metric-label">MSE</span>
                      <span className="metric-value">
                        {submission.submission_data.metrics.MSE ? submission.submission_data.metrics.MSE.toFixed(6) : '-'}
                      </span>
                    </div>

                    <div className="metric-item">
                      <span className="metric-label">RMSE</span>
                      <span className="metric-value">
                        {submission.submission_data.metrics.RMSE ? submission.submission_data.metrics.RMSE.toFixed(6) : '-'}
                      </span>
                    </div>

                    <div className="metric-item">
                      <span className="metric-label">推理时间</span>
                      <span className="metric-value">
                        {submission.submission_data.metrics.Prediction_Time ? submission.submission_data.metrics.Prediction_Time.toFixed(6) + 's' : '-'}
                      </span>
                    </div>
                  </>
                )}
              </div>

              {submission.signature && (
                <div className="signature-section">
                </div>
              )}
            </div>
            ));
          })()
        )}
      </div>
    </div>
  );
};

export default SubmissionDetails;

