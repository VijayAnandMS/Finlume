import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { DashboardPage } from './DashboardPage';
import api from '../lib/api';

const mockNavigate = vi.fn();

// Mock useNavigate from react-router-dom
vi.mock('react-router-dom', async (importOriginal) => {
  const original = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...original,
    useNavigate: () => mockNavigate,
  };
});

// Mock Recharts ResponsiveContainer to prevent width/height layout errors in jsdom
vi.mock('recharts', async (importOriginal) => {
  const original = await importOriginal<typeof import('recharts')>();
  return {
    ...original,
    ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  };
});

// Mock api module
vi.mock('../lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
    put: vi.fn(),
  },
}));

describe('DashboardPage component', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('redirects to /login if no token is present', async () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  it('loads and displays user data and financial summaries', async () => {
    localStorage.setItem('token', 'fake-jwt-token');

    vi.mocked(api.get).mockImplementation((url) => {
      if (url === '/api/auth/me') {
        return Promise.resolve({ data: { username: 'vijay' } });
      }
      if (url === '/api/summary/') {
        return Promise.resolve({
          data: {
            total_income: 75000.0,
            total_expense: 25000.0,
            net: 50000.0,
            top_categories: [{ category: 'Rent', amount: 20000.0 }],
            transactions: [
              {
                id: 1,
                user_id: 1,
                date: '2026-07-08',
                category: 'Rent',
                type: 'expense',
                amount: 20000.0,
                description: 'Rent payment',
                created_at: '2026-07-08T12:00:00Z',
              },
            ],
          },
        });
      }
      if (url === '/api/transactions/') {
        return Promise.resolve({ data: [] });
      }
      return Promise.reject(new Error('Not found'));
    });

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    // Wait for the mock API data to be fetched and displayed on screen
    await waitFor(() => {
      expect(screen.getByText(/Hi, vijay/i)).toBeInTheDocument();
      expect(screen.getByText(/₹75,000/i)).toBeInTheDocument(); // Income card
      expect(screen.getByText(/₹25,000/i)).toBeInTheDocument(); // Expense card
      expect(screen.getByText(/₹50,000/i)).toBeInTheDocument(); // Net surplus card
      expect(screen.getByText(/Rent payment/i)).toBeInTheDocument(); // Transaction table entry
    });
  });
  it('renders advisor tab and submits chat', async () => {
    localStorage.setItem('token', 'fake-jwt-token');

    vi.mocked(api.get).mockImplementation((url) => {
      if (url === '/api/auth/me') return Promise.resolve({ data: { username: 'testuser' } });
      if (url === '/api/summary/') return Promise.resolve({ data: { total_income: 0, total_expense: 0, net: 0, top_categories: [], transactions: [] } });
      if (url === '/api/transactions/') return Promise.resolve({ data: [] });
      return Promise.reject(new Error('Not found'));
    });
    
    vi.mocked(api.post).mockImplementation((url) => {
      if (url === '/api/agents/advisor') {
        return Promise.resolve({
          data: {
            answer: "Here is your reasoning.",
            recommendation: "Purchase approved.",
            affordability_score: "Excellent",
            savings_rate: "25%",
            emergency_fund_status: "4 months",
            risk_level: "Low Risk",
            calculations: {}
          }
        });
      }
      return Promise.reject(new Error('Not found'));
    });

    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    );

    // Switch to Advisor Tab
    await waitFor(() => {
      const advisorTab = screen.getByRole('button', { name: /Advisor/i });
      fireEvent.click(advisorTab);
    });

    // Check if initial placeholder renders
    expect(screen.getByText(/Ask for Financial Advice/i)).toBeInTheDocument();

    // Type and submit question
    const input = screen.getByPlaceholderText(/Can I afford a bike/i);
    const submitBtn = screen.getByRole('button', { name: /Ask Advisor/i });
    
    fireEvent.change(input, { target: { value: 'Can I afford a bike?' } });
    fireEvent.click(submitBtn);

    // Verify API called and loading state triggered
    expect(api.post).toHaveBeenCalledWith('/api/agents/advisor', { question: 'Can I afford a bike?' });
    
    // Wait for response cards to render
    await waitFor(() => {
      expect(screen.getByText('Purchase approved.')).toBeInTheDocument();
      expect(screen.getByText('Excellent')).toBeInTheDocument();
      expect(screen.getByText('25%')).toBeInTheDocument();
      expect(screen.getByText('4 months')).toBeInTheDocument();
      expect(screen.getByText('Low Risk')).toBeInTheDocument();
    });
  });
});
