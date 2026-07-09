import { describe, it, expect, beforeEach, vi } from 'vitest';
import api from './api';

describe('api axios instance', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('should have baseURL matching VITE_API_BASE_URL or fallback', () => {
    expect(api.defaults.baseURL).toBe('http://localhost:8000');
  });

  it('should attach Authorization header when token exists in localStorage', async () => {
    localStorage.setItem('token', 'test-token');
    
    // Retrieve the registered request interceptor
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const interceptor = (api.interceptors.request as any).handlers[0];
    const config = {
      headers: {}
    };
    
    const resultConfig = await interceptor.fulfilled(config);
    expect(resultConfig.headers.Authorization).toBe('Bearer test-token');
  });

  it('should not attach Authorization header when no token exists in localStorage', async () => {
    // Retrieve the registered request interceptor
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const interceptor = (api.interceptors.request as any).handlers[0];
    const config = {
      headers: {}
    };
    
    const resultConfig = await interceptor.fulfilled(config);
    expect(resultConfig.headers.Authorization).toBeUndefined();
  });
});
