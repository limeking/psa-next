import ModuleTreePage from './modules/sysadmin/pages/ModuleTreePage';
import SystemStatusPage from './modules/sysadmin/pages/SystemStatusPage';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function App() {
  return (
    <Router>
      <Routes>
          <Route path="/sysadmin/module-tree" element={<ModuleTreePage />} />
          <Route path="/sysadmin/status" element={<SystemStatusPage />} />
        {/* Route will be auto-injected by automation */}
      </Routes>
    </Router>
  );
}
export default App;
