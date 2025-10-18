import React, { useState, useEffect } from 'react';
import { getStudentSubmissions } from '../api/api';
import './SubmissionDetails.css';

const SubmissionDetails = ({ studentId, assignmentId, onClose }) => {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 自动刷新相关状态
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5);
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

  // 自动刷新定时器
  useEffect(() => {
    if (!autoRefresh || !studentId || !assignmentId) return;

    const timer = setInterval(() => {
      fetchSubmissions(false); // 后台刷新，不显示loading
    }, refreshInterval * 1000);

    return () => clearInterval(timer);
  }, [autoRefresh, refreshInterval, studentId, assignmentId]);

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

      <div className="details-controls">
        <div className="refresh-controls">
          <label className="refresh-label">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            <span>自动刷新</span>
          </label>
          
          {autoRefresh && (
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="interval-select"
            >
              <option value={3}>3秒</option>
              <option value={5}>5秒</option>
              <option value={10}>10秒</option>
              <option value={30}>30秒</option>
            </select>
          )}
          
          <button
            className="manual-refresh-button"
            onClick={() => fetchSubmissions()}
            disabled={loading}
            title="手动刷新"
          >
            ↻
          </button>
        </div>
        
        {lastUpdate && (
          <div className="last-update">
            最后更新: {formatLastUpdate()}
          </div>
        )}
      </div>

      <div className="submissions-list">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : error ? (
          <div className="error-message">{error}</div>
        ) : submissions.length === 0 ? (
          <div className="empty-message">暂无提交记录</div>
        ) : (
          submissions.map((submission, index) => (
            <div key={index} className="submission-card">
              <div className="submission-header">
                <span className="submission-number">
                  第 {submission.submission_data.submission_count} 次提交
                </span>
                <span className="submission-time">
                  {formatTimestamp(submission.submission_data.timestamp)}
                </span>
              </div>

              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">MAE</span>
                  <span className="metric-value">
                    {submission.submission_data.metrics.MAE.toFixed(3)}
                  </span>
                </div>

                <div className="metric-item">
                  <span className="metric-label">MSE</span>
                  <span className="metric-value">
                    {submission.submission_data.metrics.MSE.toFixed(3)}
                  </span>
                </div>

                <div className="metric-item">
                  <span className="metric-label">RMSE</span>
                  <span className="metric-value">
                    {submission.submission_data.metrics.RMSE.toFixed(3)}
                  </span>
                </div>

                <div className="metric-item">
                  <span className="metric-label">预测时间</span>
                  <span className="metric-value">
                    {submission.submission_data.metrics.Prediction_Time.toFixed(3)}s
                  </span>
                </div>
              </div>

              {submission.signature && (
                <div className="signature-section">
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SubmissionDetails;

