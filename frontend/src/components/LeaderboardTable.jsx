import React, { useState, useEffect } from 'react';
import { getLeaderboard, getAllAssignments, getStudentsWithoutSubmission } from '../api/api';
import './LeaderboardTable.css';

const LeaderboardTable = ({ onStudentClick }) => {
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState('');
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' or 'desc'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 自动刷新（固定开启，5秒间隔）
  const refreshInterval = 5; // 固定5秒
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // 无提交记录弹窗
  const [showNoSubmissionModal, setShowNoSubmissionModal] = useState(false);
  const [noSubmissionData, setNoSubmissionData] = useState(null);
  const [loadingNoSubmission, setLoadingNoSubmission] = useState(false);

  // 初始化：获取所有作业列表（从assignments.json）
  useEffect(() => {
    const fetchAssignments = async () => {
      try {
        const allAssignments = await getAllAssignments();
        const assignmentIds = Object.keys(allAssignments);
        setAssignments(assignmentIds);
        
        // 默认选择第一个作业
        if (assignmentIds.length > 0) {
          setSelectedAssignment(assignmentIds[0]);
        }
      } catch (err) {
        console.error('Failed to fetch assignments:', err);
        setError('无法加载作业列表');
      }
    };

    fetchAssignments();
  }, []);

  // 获取排行榜数据的函数（提取出来以便复用）
  const fetchLeaderboard = async (showLoading = true) => {
    if (!selectedAssignment) return;
    
    if (showLoading) setLoading(true);
    setError(null);
    try {
      const data = await getLeaderboard(selectedAssignment);
      setLeaderboardData(data);
      setLastUpdate(new Date());
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err);
      setError('无法加载排行榜数据');
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  // 当选择的作业改变时，获取对应的排行榜数据
  useEffect(() => {
    fetchLeaderboard();
  }, [selectedAssignment]);

  // 自动刷新定时器（固定每5秒）
  useEffect(() => {
    if (!selectedAssignment) return;

    const timer = setInterval(() => {
      fetchLeaderboard(false); // 后台刷新，不显示loading
    }, refreshInterval * 1000);

    return () => clearInterval(timer);
  }, [selectedAssignment]);

  // 切换排序顺序
  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  // 根据排序顺序处理数据
  // 排序优先级：1. RMSE分数（越小越好）2. 推理时间（越小越好）
  const sortedData = [...leaderboardData].sort((a, b) => {
    // 首先按分数（RMSE）排序 - 越小越好
    if (a.score !== b.score) {
      return sortOrder === 'asc' ? a.score - b.score : b.score - a.score;
    }
    
    // 分数相同时，按推理时间排序 - 越小越好
    if (a.metrics.Prediction_Time !== b.metrics.Prediction_Time) {
      return sortOrder === 'asc' 
        ? a.metrics.Prediction_Time - b.metrics.Prediction_Time 
        : b.metrics.Prediction_Time - a.metrics.Prediction_Time;
    }
    
    // 推理时间也相同时，保持原有顺序
    return 0;
  });

  // 格式化时间戳
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
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

  const handleStudentClick = (studentId) => {
    onStudentClick(studentId, selectedAssignment);
  };

  // 获取无提交记录的学生
  const fetchNoSubmissionStudents = async () => {
    if (!selectedAssignment) return;
    
    setLoadingNoSubmission(true);
    try {
      const data = await getStudentsWithoutSubmission(selectedAssignment);
      setNoSubmissionData(data);
      setShowNoSubmissionModal(true);
    } catch (err) {
      console.error('Failed to fetch students without submission:', err);
      alert('获取未提交学生列表失败');
    } finally {
      setLoadingNoSubmission(false);
    }
  };

  // 将学号列表分成四列，每列最多40个
  const formatStudentColumns = (studentIds) => {
    const columns = [[], [], [], []];
    studentIds.forEach((id, index) => {
      const columnIndex = Math.floor(index / 40);
      if (columnIndex < 4) {
        columns[columnIndex].push(id);
      }
    });
    return columns;
  };

  if (error) {
    return (
      <div className="leaderboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <h1 className="leaderboard-title">DaSE ML-2025 Assignment Performance Leaderboard</h1>
        
        <div className="assignment-selector">
          <label htmlFor="assignment-select">作业：</label>
          <select
            id="assignment-select"
            value={selectedAssignment}
            onChange={(e) => setSelectedAssignment(e.target.value)}
            className="assignment-dropdown"
          >
            {assignments.map((assignmentId) => (
              <option key={assignmentId} value={assignmentId}>
                Assignment {assignmentId}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="table-wrapper">
        <div className="table-controls">
          <div className="controls-left">
            <button 
              className="sort-button"
              onClick={toggleSortOrder}
              title={sortOrder === 'asc' ? '切换为倒序' : '切换为正序'}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
            <button 
              className="no-submission-button"
              onClick={fetchNoSubmissionStudents}
              disabled={loadingNoSubmission || !selectedAssignment}
              title="查看未提交学生名单"
            >
              无提交记录
            </button>
          </div>
          
          <div className="controls-right">
            {lastUpdate && (
              <div className="last-update">
                自动刷新中 · 最后更新: {formatLastUpdate()}
              </div>
            )}
          </div>
        </div>

        {loading ? (
          <div className="loading">加载中...</div>
        ) : (
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th>排名</th>
                <th>学号</th>
                <th>昵称</th>
                <th><strong>RMSE</strong></th>
                <th><strong>推理时间</strong></th>
                <th>MAE</th>
                <th>MSE</th>
                <th>最后提交时间</th>
                <th>提交次数</th>
              </tr>
            </thead>
            <tbody>
              {sortedData.map((entry, index) => (
                <tr key={entry.student_info.student_id}>
                  <td className="rank-cell">{sortOrder === 'asc' ? index + 1 : sortedData.length - index}</td>
                  <td 
                    className="student-id-cell"
                    onClick={() => handleStudentClick(entry.student_info.student_id)}
                  >
                    {entry.student_info.student_id}
                  </td>
                  <td className="name-cell">
                    {entry.student_info.nickname || entry.student_info.name || '-'}
                  </td>
                  <td className="score-cell bold-cell">{entry.score.toFixed(6)}</td>
                  <td className="prediction-time-cell bold-cell">{entry.metrics.Prediction_Time.toFixed(6)}s</td>
                  <td className="mae-cell">{entry.metrics.MAE.toFixed(6)}</td>
                  <td className="mse-cell">{entry.metrics.MSE.toFixed(6)}</td>
                  <td className="time-cell">{formatTimestamp(entry.timestamp)}</td>
                  <td className="count-cell">{entry.submission_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {!loading && sortedData.length === 0 && (
          <div className="empty-message">暂无数据</div>
        )}
      </div>

      {/* 无提交记录弹窗 */}
      {showNoSubmissionModal && noSubmissionData && (
        <div className="modal-overlay" onClick={() => setShowNoSubmissionModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>以下同学暂无提交记录（{noSubmissionData.count}人）</h3>
              <button 
                className="modal-close-button"
                onClick={() => setShowNoSubmissionModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="student-columns">
                {formatStudentColumns(noSubmissionData.student_ids).map((column, colIndex) => (
                  <div key={colIndex} className="student-column">
                    {column.map((studentId, index) => (
                      <div key={index} className="student-id-item">
                        {studentId}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeaderboardTable;

