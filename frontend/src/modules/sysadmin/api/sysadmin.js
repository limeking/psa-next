export async function fetchSystemStatus() {
  const res = await fetch('/sysadmin/status');
  return await res.json();
}