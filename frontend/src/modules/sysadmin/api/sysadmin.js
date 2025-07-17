export async function fetchSystemStatus() {
  const res = await fetch('/api/sysadmin/status');
  return await res.json();
}
