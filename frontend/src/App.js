import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AdminPage from './modules/admin';
import SystemStatusPage from './modules/sysadmin/pages/SystemStatusPage';

function App() {
  return (
    <Router>
      <Routes>
          <Route path="/admin" element={ <AdminPage /> } />
        {/* Route will be auto-injected by automation */}
          <Route path="/sysadmin/status" element={<SystemStatusPage />} />
      </Routes>
    </Router>
  );
}
export default App;
