import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { ProtectedRoute } from './components/ProtectedRoute';

const LandingPage = React.lazy(() => import('./pages/LandingPage').then(m => ({ default: m.LandingPage })));
const LoginPage = React.lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = React.lazy(() => import('./pages/RegisterPage').then(m => ({ default: m.RegisterPage })));
const ForgotPasswordPage = React.lazy(() => import('./pages/ForgotPasswordPage').then(m => ({ default: m.ForgotPasswordPage })));
const ResetPasswordPage = React.lazy(() => import('./pages/ResetPasswordPage').then(m => ({ default: m.ResetPasswordPage })));
const DashboardPage = React.lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const TransactionsPage = React.lazy(() => import('./pages/TransactionsPage').then(m => ({ default: m.TransactionsPage })));
const IntelligenceDashboard = React.lazy(() => import('./pages/IntelligenceDashboard').then(m => ({ default: m.default })));
const ImportWorkflowPage = React.lazy(() => import('./pages/ImportWorkflowPage').then(m => ({ default: m.ImportWorkflowPage })));
const ReceiptPreviewPage = React.lazy(() => import('./pages/ReceiptPreviewPage').then(m => ({ default: m.default })));
const ReceiptHistoryPage = React.lazy(() => import('./pages/ReceiptHistoryPage').then(m => ({ default: m.default })));
const ImportHistoryPage = React.lazy(() => import('./pages/ImportHistoryPage').then(m => ({ default: m.ImportHistoryPage })));
const ImportDetailsPage = React.lazy(() => import('./pages/ImportDetailsPage').then(m => ({ default: m.ImportDetailsPage })));
const InsightsDashboard = React.lazy(() => import('./pages/InsightsDashboard').then(m => ({ default: m.InsightsDashboard })));


function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="flex h-screen items-center justify-center bg-slate-950 text-slate-400">Loading App Core...</div>}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/transactions" element={<ProtectedRoute><TransactionsPage /></ProtectedRoute>} />
          <Route path="/intelligence" element={<ProtectedRoute><IntelligenceDashboard /></ProtectedRoute>} />
          <Route path="/imports/:session_id/workflow" element={<ProtectedRoute><ImportWorkflowPage /></ProtectedRoute>} />
          <Route path="/receipts/:receipt_session_id/preview" element={<ProtectedRoute><ReceiptPreviewPage /></ProtectedRoute>} />
          <Route path="/receipts/history" element={<ProtectedRoute><ReceiptHistoryPage /></ProtectedRoute>} />
          <Route path="/import/history" element={<ProtectedRoute><ImportHistoryPage /></ProtectedRoute>} />
          <Route path="/import/history/:sessionId" element={<ProtectedRoute><ImportDetailsPage /></ProtectedRoute>} />
          <Route path="/insights" element={<ProtectedRoute><InsightsDashboard /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />

        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
