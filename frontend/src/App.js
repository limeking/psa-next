import AdminPage from './modules/admin';
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path="/admin" element={ <AdminPage /> } />
          <Route path="/admin" element={ <AdminPage /> } />
        <Route path="/" element={
          <div style={{textAlign: "center", marginTop: "5em"}}>
            <h2>Welcome to PSA-NEXT</h2>
            <p>메인 페이지입니다.</p>
            <a href="/admin">Admin 대시보드로 이동</a>
          </div>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
