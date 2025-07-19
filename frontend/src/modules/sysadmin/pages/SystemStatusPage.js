import React, { useEffect, useState, useRef } from 'react';
import { fetchSystemStatus, fetchModuleList, fetchEvents, createModule, deleteModule, restartBackend } from '../api/sysadmin';

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

// 에러/이벤트 로그 (강조/알림/자동 새로고침)
function EventLog() {
  const [events, setEvents] = useState([]);
  const [lastError, setLastError] = useState(null);
  const mountedRef = useRef(false); // ⭐️ 추가

  useEffect(() => {
    fetchEvents().then(res => {
      setEvents(res.events || []);
      const err = (res.events || []).find(e => (e.message || "").includes("ERROR"));
      if (err && (!lastError || lastError !== err.message)) {
        // ⭐️ 마운트 직후 첫 실행일 땐 alert 안 띄움
        if (mountedRef.current) {
          window.alert(`에러 발생: ${err.message}`);
        }
        setLastError(err.message);
      }
      mountedRef.current = true; // ⭐️ 첫 렌더 이후로 변경
    });
    const timer = setInterval(() => {
      fetchEvents().then(res => {
        setEvents(res.events || []);
        const err = (res.events || []).find(e => (e.message || "").includes("ERROR"));
        if (err && (!lastError || lastError !== err.message)) {
          window.alert(`에러 발생: ${err.message}`);
          setLastError(err.message);
        }
      });
    }, 5000);
    return () => clearInterval(timer);
  }, [lastError]);

  if (!events.length) return <div>이벤트 없음</div>;
  return (
    <div>
      <h3>최근 이벤트/에러 로그</h3>
      <ul>
        {events.map((e, idx) => (
          <li key={idx} style={{
            color: e.message.includes('ERROR') ? '#e94040' :
                   e.message.includes('WARN') ? '#ffb100' : 'black',
            fontWeight: e.message.includes('ERROR') ? 'bold' : 'normal',
            background: e.message.includes('ERROR') ? '#ffe0e0' : 'none',
            borderRadius: "5px",
            padding: "2px 6px",
            marginBottom: "2px"
          }}>
            {e.message}
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
  const [restartStatus, setRestartStatus] = useState(null);

  useEffect(() => {
    fetchSystemStatus()
      .then((data) => setStatus(data))
      .catch((err) => setStatus({ error: err.message }))
      .finally(() => setLoading(false));
    const timer = setInterval(() => {
      fetchSystemStatus().then(setStatus);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  if (loading) return <div>로딩중...</div>;
  if (status.error) return <div>에러: {status.error}</div>;

  const handleRestart = async () => {
    setRestartStatus("서버 리스타트 진행중...");
    const res = await restartBackend();
    if (res.success) setRestartStatus("서버 리스타트 완료!");
    else setRestartStatus("에러: " + (res.stderr || res.error));
  };

  return (
    <div>
      <h2>시스템 상태 (환경: {status.env})</h2>
    <ModuleManager />
    <button onClick={handleRestart} style={{marginBottom: 16}} disabled>
      서버 리스타트
    </button>
    {restartStatus && <div>{restartStatus}</div>}
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
