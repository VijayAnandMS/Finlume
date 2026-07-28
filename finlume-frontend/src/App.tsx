import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

const LoginPage = React.lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = React.lazy(() => import('./pages/RegisterPage').then(m => ({ default: m.RegisterPage })));
const VerifyEmailPage = React.lazy(() => import('./pages/VerifyEmailPage').then(m => ({ default: m.VerifyEmailPage })));
const ForgotPasswordPage = React.lazy(() => import('./pages/ForgotPasswordPage').then(m => ({ default: m.ForgotPasswordPage })));
const ResetPasswordPage = React.lazy(() => import('./pages/ResetPasswordPage').then(m => ({ default: m.ResetPasswordPage })));
const DashboardPage = React.lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const TransactionsPage = React.lazy(() => import('./pages/TransactionsPage').then(m => ({ default: m.TransactionsPage })));
const IntelligenceDashboard = React.lazy(() => import('./pages/IntelligenceDashboard').then(m => ({ default: m.default })));
const ImportWorkflowPage = React.lazy(() => import('./pages/ImportWorkflowPage').then(m => ({ default: m.ImportWorkflowPage })));
const ImportHistoryPage = React.lazy(() => import('./pages/ImportHistoryPage').then(m => ({ default: m.ImportHistoryPage })));
const ImportDetailsPage = React.lazy(() => import('./pages/ImportDetailsPage').then(m => ({ default: m.ImportDetailsPage })));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="flex h-screen items-center justify-center bg-slate-950 text-slate-400">Loading App Core...</div>}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/intelligence" element={<IntelligenceDashboard />} />
          <Route path="/import/preview/:sessionId" element={<ImportWorkflowPage />} />
          <Route path="/import/history" element={<ImportHistoryPage />} />
          <Route path="/import/history/:sessionId" element={<ImportDetailsPage />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
