import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import App from './App';

// Mock api module to avoid actual network calls during testing
vi.mock('./lib/api', () => {
  return {
    default: {
      get: vi.fn((url) => {
        if (url === '/api/auth/me') {
          return Promise.resolve({ data: { username: 'testuser' } });
        }
        if (url === '/api/summary/') {
          return Promise.resolve({
            data: {
              total_income: 1000,
              total_expense: 500,
              net: 500,
              top_categories: [],
              transactions: []
            }
          });
        }
        if (url === '/api/transactions/') {
          return Promise.resolve({ data: [] });
        }
        return Promise.reject(new Error('Not found'));
      }),
      post: vi.fn()
    }
  };
});

describe('App Routing', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders LoginPage on /login route', () => {
    window.history.pushState({}, '', '/login');
    render(<App />);
    expect(screen.getByText(/Your personal AI-driven financial copilot/i)).toBeInTheDocument();
  });

  it('renders DashboardPage on /dashboard route when token exists', async () => {
    localStorage.setItem('token', 'fake-jwt-token');
    window.history.pushState({}, '', '/dashboard');
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/Hi, testuser/i)).toBeInTheDocument();
    });
  });

  it('redirects to /login on an unknown route like /foo', () => {
    window.history.pushState({}, '', '/foo');
    render(<App />);
    expect(screen.getByText(/Your personal AI-driven financial copilot/i)).toBeInTheDocument();
    expect(window.location.pathname).toBe('/login');
  });
});

