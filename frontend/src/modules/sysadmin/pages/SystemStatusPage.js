import React, { useEffect, useState, useRef, useCallback } from 'react';
import { fetchSystemStatus, fetchModuleList, fetchEvents, createModule, deleteModule } from '../api/sysadmin';
import { useEventSocket } from '../hooks/useEventSocket'; // 이 줄 추가

// 상태 뱃지 (컬러/강조)
function StatusBadge({ status }) {
  let color = "gray";
  if (status === "OK" || status === "running") color = "#36ba46";
  else if (status === "FAIL" || status === "exited") color = "#e94040";
  else if (status === "starting") color = "#ffb100";
  return (
    <span style={{
      display: "inline-block",
      minWidth: 48,
      padding: "2px 8px",
      borderRadius: "8px",
      background: color,
      color: "#fff",
      marginRight: 4,
      fontWeight: "bold",
      boxShadow: status === "FAIL" || status === "exited" ? "0 0 8px 2px #e9404066" : "none",
      transition: "background 0.3s"
    }}>
      {status}
    </span>
  );
}

// 모듈 생성/삭제 컴포넌트
function ModuleManager() {
  const [moduleName, setModuleName] = useState('');
  const [result, setResult] = useState(null);

  const handleCreate = async () => {
    setResult(null);
    const res = await createModule(moduleName);
    setResult(res);
  };

  const handleDelete = async () => {
    setResult(null);
    const res = await deleteModule(moduleName);
    setResult(res);
  };

  return (
    <div style={{margin: "2em 0", padding: "1em", border: "1px solid #ddd", borderRadius: "8px"}}>
      <h3>모듈 생성/삭제</h3>
      <input
        type="text"
        value={moduleName}
        onChange={e => setModuleName(e.target.value)}
        placeholder="모듈명"
        style={{marginRight: "1em"}}
      />
      <button onClick={handleCreate}>생성</button>
      <button onClick={handleDelete} style={{marginLeft: "1em"}}>삭제</button>
      {result && (
        <pre style={{marginTop: "1em", background: "#f8f8f8", padding: "1em", borderRadius: "6px"}}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

// 모듈 리스트 테이블 (상태 뱃지 적용)
function ModuleList() {
  const [modules, setModules] = useState([]);
  useEffect(() => {
    fetchModuleList().then(setModules);
    const timer = setInterval(() => fetchModuleList().then(setModules), 4000);
    return () => clearInterval(timer);
  }, []);
  if (!modules.length) return <div>모듈 없음</div>;
  return (
    <div>
      <h3>모듈 현황</h3>
      <table>
        <thead>
          <tr>
            <th>이름</th>
            <th>Backend</th>
            <th>Frontend</th>
            <th>DB</th>
            <th>Enabled</th>
            <th>Route</th>
          </tr>
        </thead>
        <tbody>
          {modules.map(m => (
            <tr key={m.name}>
              <td>{m.name}</td>
              <td>{m.backend ? <StatusBadge status="OK" /> : "-"}</td>
              <td>{m.frontend ? <StatusBadge status="OK" /> : "-"}</td>
              <td>{m.db ? <StatusBadge status="OK" /> : "-"}</td>
              <td>{m.enabled ? "Y" : "N"}</td>
              <td>{m.route}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


// ⭐️ WebSocket 실시간 이벤트/에러 로그
function EventLog() {
  const [events, setEvents] = useState([]);
  const [lastError, setLastError] = useState(null);
  const mountedRef = useRef(false);

  // 최초 1회 기존 REST로 이벤트 가져오기 (fallback)
  useEffect(() => {
    fetchEvents().then(res => {
      setEvents(res.events || []);
      const err = (res.events || []).find(e => (e.message || "").includes("ERROR"));
      if (err && (!lastError || lastError !== err.message)) {
        if (mountedRef.current) window.alert(`에러 발생: ${err.message}`);
        setLastError(err.message);
      }
      mountedRef.current = true;
    });
  }, []);

  // ⭐️ WebSocket으로 실시간 이벤트 받기
  useEventSocket((msg) => {
    setEvents(prev => [msg, ...prev].slice(0, 30)); // 최근 30개 유지
    if ((msg.type === "error" || (msg.message || "").includes("ERROR")) && lastError !== msg.message) {
      window.alert(`에러 발생: ${msg.message}`);
      setLastError(msg.message);
    }
  });

  if (!events.length) return <div>이벤트 없음</div>;
  return (
    <div>
      <h3>최근 이벤트/에러 로그</h3>
      <ul>
        {events.map((e, idx) => (
          <li key={idx} style={{
            color: e.type === "error" || (e.message || "").includes('ERROR') ? '#e94040' :
                  (e.type === "warn" || (e.message || "").includes('WARN')) ? '#ffb100' : 'black',
            fontWeight: e.type === "error" ? 'bold' : 'normal',
            background: e.type === "error" ? '#ffe0e0' : 'none',
            borderRadius: "5px",
            padding: "2px 6px",
            marginBottom: "2px"
          }}>
            [{e.timestamp?.slice(11,19) || ''}] {e.message}
          </li>
        ))}
      </ul>
    </div>
  );
}


// 메인 시스템 상태 페이지 (실시간 새로고침)
function SystemStatusPage() {
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [events, setEvents] = useState([]);
  const [lastError, setLastError] = useState(null);
  const mountedRef = useRef(false);

  useEffect(() => {
    fetchSystemStatus()
      .then((data) => setStatus(data))
      .catch((err) => setStatus({ error: err.message }))
      .finally(() => setLoading(false));
    const timer = setInterval(() => {
      fetchSystemStatus().then(setStatus);
    }, 3000);
    fetchEvents().then(res => {
      setEvents(res.events || []);
      const err = (res.events || []).find(e => (e.message || "").includes("ERROR"));
      if (err && (!lastError || lastError !== err.message)) {
        if (mountedRef.current) window.alert(`에러 발생: ${err.message}`);
        setLastError(err.message);
      }
      mountedRef.current = true;
    });
    return () => clearInterval(timer);
  }, []);

  // ⭐️ WebSocket 연결은 여기서 한 번만!
  const handleEvent = useCallback((msg) => {
    setEvents(prev => [msg, ...prev].slice(0, 30));
    if ((msg.type === "error" || (msg.message || "").includes("ERROR")) && lastError !== msg.message) {
      window.alert(`에러 발생: ${msg.message}`);
      setLastError(msg.message);
    }
  }, [lastError]);
  useEventSocket(handleEvent);

  return (
    <div>
      <h2>시스템 상태 (환경: {status.env})</h2>
    <ModuleManager />

      <table>
        <thead>
          <tr>
            <th>컨테이너</th><th>상태</th><th>이미지</th><th>ID</th>
          </tr>
        </thead>
        <tbody>
          {status.containers && status.containers.map((c, i) => (
            <tr key={c.name || i}>
              <td>{c.name}</td>
              <td><StatusBadge status={c.status} /></td>
              <td>{c.image ? c.image : '-'}</td>
              <td>{c.id ? c.id : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ModuleList />
      <EventLog />
    </div>
  );
}

export default SystemStatusPage;
