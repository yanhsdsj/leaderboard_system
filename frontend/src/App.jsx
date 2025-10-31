import React, { useState } from 'react';
import LeaderboardTable from './components/LeaderboardTable';
import SubmissionDetails from './components/SubmissionDetails';
import './App.css';

function App() {
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [assignmentConfig, setAssignmentConfig] = useState(null);

  const handleStudentClick = (studentId, assignmentId, config) => {
    setSelectedStudent(studentId);
    setSelectedAssignment(assignmentId);
    setAssignmentConfig(config);
  };

  const handleClose = () => {
    setSelectedStudent(null);
    setSelectedAssignment(null);
    setAssignmentConfig(null);
  };

  return (
    <div className="app">
      <div className="app-container">
        <LeaderboardTable onStudentClick={handleStudentClick} />
        {selectedStudent && (
          <SubmissionDetails
            studentId={selectedStudent}
            assignmentId={selectedAssignment}
            assignmentConfig={assignmentConfig}
            onClose={handleClose}
          />
        )}
      </div>
    </div>
  );
}

export default App;

