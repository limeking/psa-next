import React, { useEffect, useState } from 'react';
import { fetchSystemStatus } from '../api/sysadmin';

function SystemStatusPage() {
  const [status, setStatus] = useState(null);
  const [containers, setContainers] = useState({});  // ← 반드시 {}로 초기화!

  useEffect(() => {
    fetchSystemStatus().then((res) => {
      setStatus(res.status);
      setContainers(res.containers);
    });
  }, []);

  return (
    <div>
      <h1>System Dashboard</h1>
      <p>Status: {status}</p>
      <h2>Containers</h2>
      <div>
        {/* 값이 문자열이면 그대로, 객체면 리스트로 안전하게 출력 */}
        {containers && typeof containers === "object" && Object.keys(containers).length > 0
          ? (
            <ul>
              {Object.entries(containers).map(([name, stat]) => (
                <li key={name}><strong>{name}</strong>: {stat}</li>
              ))}
            </ul>
          )
          : (
            <span>{containers ? containers.toString() : "정보 없음"}</span>
          )
        }
      </div>
    </div>
  );
}

export default SystemStatusPage;
