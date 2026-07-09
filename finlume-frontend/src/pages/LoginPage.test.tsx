import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { LoginPage } from './LoginPage';
import api from '../lib/api';

// Mock api module
vi.mock('../lib/api', () => ({
  default: {
    post: vi.fn(),
  },
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

    expect(screen.getByText(/Your personal AI-driven financial copilot/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Sign In/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });

  it('toggles between login and register modes', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    const toggleButton = screen.getByText(/Don't have an account\? Sign Up/i);
    fireEvent.click(toggleButton);

    expect(screen.getByRole('heading', { name: /Create an Account/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign Up/i })).toBeInTheDocument();

    const backButton = screen.getByText(/Already have an account\? Sign In/i);
    fireEvent.click(backButton);

    expect(screen.getByRole('heading', { name: /Sign In/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
  });

  it('submits login data and stores token on success', async () => {
    const mockToken = 'mock-jwt-access-token';
    vi.mocked(api.post).mockResolvedValueOnce({
      data: { access_token: mockToken, token_type: 'bearer' },
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/e.g. vijay/i), {
      target: { value: 'vijay' },
    });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), {
      target: { value: 'password123' },
    });

    const submitBtn = screen.getByRole('button', { name: /Sign In/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/auth/login', {
        username: 'vijay',
        password: 'password123',
      });
      expect(localStorage.getItem('token')).toBe(mockToken);
    });
  });

  it('submits registration data and displays success alert', async () => {
    vi.mocked(api.post).mockResolvedValueOnce({
      data: { id: 1, username: 'newuser', created_at: '2026-07-08T12:00:00Z' },
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    // Switch to Sign Up mode
    fireEvent.click(screen.getByText(/Don't have an account\? Sign Up/i));

    fireEvent.change(screen.getByPlaceholderText(/e.g. vijay/i), {
      target: { value: 'newuser' },
    });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), {
      target: { value: 'password456' },
    });

    const submitBtn = screen.getByRole('button', { name: /Sign Up/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/api/auth/register', {
        username: 'newuser',
        password: 'password456',
      });
      expect(screen.getByText(/Registration successful! Please log in now./i)).toBeInTheDocument();
    });
  });

  it('displays API error details on failure', async () => {
    vi.mocked(api.post).mockRejectedValueOnce({
      response: {
        data: { detail: 'Username already registered' },
      },
    });

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    // Switch to Sign Up mode
    fireEvent.click(screen.getByText(/Don't have an account\? Sign Up/i));

    fireEvent.change(screen.getByPlaceholderText(/e.g. vijay/i), {
      target: { value: 'existinguser' },
    });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), {
      target: { value: 'password' },
    });

    fireEvent.click(screen.getByRole('button', { name: /Sign Up/i }));

    await waitFor(() => {
      expect(screen.getByText(/Username already registered/i)).toBeInTheDocument();
    });
  });
});
