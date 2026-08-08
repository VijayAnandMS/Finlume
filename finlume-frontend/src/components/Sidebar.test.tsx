import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Sidebar } from './Sidebar';

import { MemoryRouter } from 'react-router-dom';

describe('Sidebar component', () => {
  it('renders all 8 navigation labels', () => {
    render(
      <MemoryRouter>
        <Sidebar currentTab="Dashboard" onTabChange={() => {}} />
      </MemoryRouter>
    );

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
