import React, { useState, useEffect } from 'react';
import { getLeaderboard, getAllAssignments } from '../api/api';
import './LeaderboardTable.css';

const LeaderboardTable = ({ onStudentClick }) => {
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [selectedAssignment, setSelectedAssignment] = useState('');
  const [sortOrder, setSortOrder] = useState('asc'); // 'asc' or 'desc'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 自动刷新相关状态
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(5); // 默认5秒
  const [lastUpdate, setLastUpdate] = useState(null);

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

  // 自动刷新定时器
  useEffect(() => {
    if (!autoRefresh || !selectedAssignment) return;

    const timer = setInterval(() => {
      fetchLeaderboard(false); // 后台刷新，不显示loading
    }, refreshInterval * 1000);

    return () => clearInterval(timer);
  }, [autoRefresh, refreshInterval, selectedAssignment]);

  // 切换排序顺序
  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  // 根据排序顺序处理数据
  // 排序优先级：分数（RMSE）、预测时间、提交时间
  const sortedData = [...leaderboardData].sort((a, b) => {
    // 首先按分数（RMSE）排序 - 越小越好
    if (a.score !== b.score) {
      return sortOrder === 'asc' ? a.score - b.score : b.score - a.score;
    }
    
    // 分数相同时，按预测时间排序 - 越小越好
    if (a.metrics.Prediction_Time !== b.metrics.Prediction_Time) {
      return sortOrder === 'asc' 
        ? a.metrics.Prediction_Time - b.metrics.Prediction_Time 
        : b.metrics.Prediction_Time - a.metrics.Prediction_Time;
    }
    
    // 预测时间也相同时，按提交时间排序 - 越早越好
    const timeA = new Date(a.timestamp).getTime();
    const timeB = new Date(b.timestamp).getTime();
    return sortOrder === 'asc' ? timeA - timeB : timeB - timeA;
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
          </div>
          
          <div className="controls-right">
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
                  <option value={60}>60秒</option>
                </select>
              )}
              
              <button
                className="manual-refresh-button"
                onClick={() => fetchLeaderboard()}
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
        </div>

        {loading ? (
          <div className="loading">加载中...</div>
        ) : (
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th>排名</th>
                <th>学号</th>
                <th>姓名</th>
                <th>RMSE</th>
                <th>推理时间</th>
                <th>提交时间</th>
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
                  <td className="name-cell">{entry.student_info.name}</td>
                  <td className="score-cell">{entry.score.toFixed(6)}</td>
                  <td className="prediction-time-cell">{entry.metrics.Prediction_Time.toFixed(2)}s</td>
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
    </div>
  );
};

export default LeaderboardTable;

