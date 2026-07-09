import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Sidebar } from './Sidebar';

describe('Sidebar component', () => {
  it('renders all 8 navigation labels', () => {
    render(<Sidebar />);
    
    const expectedLabels = [
      'Dashboard',
      'AI Chat',
      'Transactions',
      'Budget',
      'Goals',
      'Investments',
      'Reports',
      'Settings',
    ];
    
    expectedLabels.forEach((label) => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });
});
