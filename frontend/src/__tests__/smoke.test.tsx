import { render, screen } from '@testing-library/react';

describe('smoke', () => {
  it('renders a basic element', () => {
    render(<div>Agentic Commerce</div>);
    expect(screen.getByText('Agentic Commerce')).toBeInTheDocument();
  });
});
