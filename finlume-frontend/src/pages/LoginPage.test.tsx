import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { LoginPage } from './LoginPage';

vi.mock('../services/api', () => ({
  default: {
    customLogin: vi.fn(),
  },
  api: {
    customLogin: vi.fn(),
  }
}));

describe('LoginPage component', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders sign in form by default', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(screen.getByText(/Access your financial intelligence copilot./i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Welcome Back/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Username or Email Address/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
  });

  it('submits login data and stores token on success', async () => {
    const mockToken = 'mock-jwt-access-token';
    const { api } = await import('../services/api');
    vi.mocked(api.customLogin).mockResolvedValueOnce({
      access_token: mockToken,
      token_type: 'bearer',
      id: 1,
      username: 'vijay',
      created_at: ''
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Username or Email Address/i), {
      target: { value: 'vijay' },
    });
    fireEvent.change(screen.getByPlaceholderText(/Password/i), {
      target: { value: 'password123' },
    });

    const submitBtn = screen.getByRole('button', { name: /Sign In/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(api.customLogin).toHaveBeenCalledWith('vijay', 'password123');
      expect(localStorage.getItem('token')).toBe(mockToken);
    });
  });

  it('displays API error details on failure', async () => {
    const { api } = await import('../services/api');
    vi.mocked(api.customLogin).mockRejectedValueOnce({
      response: {
        data: { detail: 'Authentication failed' },
      },
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Username or Email Address/i), {
      target: { value: 'existinguser' },
    });
    fireEvent.change(screen.getByPlaceholderText(/Password/i), {
      target: { value: 'password' },
    });

    fireEvent.click(screen.getByRole('button', { name: /Sign In/i }));

    await waitFor(() => {
      expect(screen.getByText(/Authentication failed/i)).toBeInTheDocument();
    });
  });
});
