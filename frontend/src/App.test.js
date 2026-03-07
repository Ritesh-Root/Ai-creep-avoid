import { render, screen } from '@testing-library/react';
import App from './App';

test('renders SmartShield header', () => {
  render(<App />);
  const heading = screen.getByText(/SmartShield AI/i);
  expect(heading).toBeInTheDocument();
});
