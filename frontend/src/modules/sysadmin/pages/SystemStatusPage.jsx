import React, { useEffect, useState } from 'react';
import { fetchSystemStatus } from '../api/sysadmin';

function SystemStatusPage() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    fetchSystemStatus().then((res) => setStatus(res.status));
  }, []);

  return (
    <div>
      <h1>System Dashboard</h1>
      <p>Status: {status}</p>
    </div>
  );
}
export default SystemStatusPage;