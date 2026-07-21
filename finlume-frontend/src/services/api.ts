import axiosInstance from '../lib/api';

export const api = {
    customLogin: async (identity: string, password: string) => {
        const res = await axiosInstance.post('/api/auth/custom-login', { identity, password });
        return res.data;
    },
    register: async (full_name: string, username: string, email: string, password: string, phone_number?: string) => {
        const res = await axiosInstance.post('/api/auth/register', { full_name, username, email, password, phone_number });
        return res.data;
    },
    verifyEmail: async (email: string, otp: string) => {
        const res = await axiosInstance.post('/api/auth/verify-email', { email, otp });
        return res.data;
    },
    resendOTP: async (email: string) => {
        const res = await axiosInstance.post('/api/auth/resend-otp', { email });
        return res.data;
    },
    forgotPassword: async (email: string) => {
        const res = await axiosInstance.post('/api/auth/forgot-password', { email });
        return res.data;
    },
    resetPassword: async (token: string, new_password: string) => {
        const res = await axiosInstance.post('/api/auth/reset-password', { token, new_password });
        return res.data;
    },
    updateProfile: async (data: any) => {
        const res = await axiosInstance.put('/api/profile/', data);
        return res.data;
    },
    getProfile: async () => {
        const res = await axiosInstance.get('/api/profile/');
        return res.data;
    }
};
