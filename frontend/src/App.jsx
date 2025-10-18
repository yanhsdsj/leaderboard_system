import React, { useState } from 'react';
import LeaderboardTable from './components/LeaderboardTable';
import SubmissionDetails from './components/SubmissionDetails';
import './App.css';

function App() {
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedAssignment, setSelectedAssignment] = useState(null);

  const handleStudentClick = (studentId, assignmentId) => {
    setSelectedStudent(studentId);
    setSelectedAssignment(assignmentId);
  };

  const handleClose = () => {
    setSelectedStudent(null);
    setSelectedAssignment(null);
  };

  return (
    <div className="app">
      <div className="app-container">
        <LeaderboardTable onStudentClick={handleStudentClick} />
        {selectedStudent && (
          <SubmissionDetails
            studentId={selectedStudent}
            assignmentId={selectedAssignment}
            onClose={handleClose}
          />
        )}
      </div>
    </div>
  );
}

export default App;

