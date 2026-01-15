/**
 * Jest Setup Library Verification Test
 * =====================================
 *
 * Tests to verify the jest-setup-collection library is working correctly.
 */

import React from 'react';
import { render, renderHook, createTestQueryClient } from '@testing/test-utils';
import { screen } from '@testing-library/react';

// Test component
function TestButton({ onClick, children }: { onClick?: () => void; children: React.ReactNode }) {
  return (
    <button onClick={onClick} type="button">
      {children}
    </button>
  );
}

// Test hook
function useCounter(initial = 0) {
  const [count, setCount] = React.useState(initial);
  const increment = () => setCount((c) => c + 1);
  return { count, increment };
}

describe('Jest Setup Library', () => {
  describe('render utility', () => {
    it('renders components with providers', () => {
      render(<TestButton>Click Me</TestButton>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    it('supports user interactions', async () => {
      const onClick = jest.fn();
      render(<TestButton onClick={onClick}>Submit</TestButton>);

      const button = screen.getByRole('button', { name: /submit/i });
      await button.click();

      expect(onClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('renderHook utility', () => {
    it('renders hooks with providers', () => {
      const { result } = renderHook(() => useCounter(5));
      expect(result.current.count).toBe(5);
    });

    it('updates hook state correctly', () => {
      const { result } = renderHook(() => useCounter(0));

      // Initial value
      expect(result.current.count).toBe(0);
    });
  });

  describe('createTestQueryClient', () => {
    it('creates a query client configured for testing', () => {
      const client = createTestQueryClient();
      const options = client.getDefaultOptions();

      expect(options.queries?.retry).toBe(false);
      expect(options.queries?.refetchOnWindowFocus).toBe(false);
    });
  });

  describe('custom matchers', () => {
    it('toBeValidJSON works correctly', () => {
      expect('{"key": "value"}').toBeValidJSON();
      expect('not json').not.toBeValidJSON();
    });

    it('toBeWithinRange works correctly', () => {
      expect(5).toBeWithinRange(1, 10);
      expect(15).not.toBeWithinRange(1, 10);
    });

    it('toBeSorted works correctly', () => {
      expect([1, 2, 3, 4, 5]).toBeSorted();
      expect(['a', 'b', 'c']).toBeSorted();
      expect([3, 1, 2]).not.toBeSorted();
    });

    it('toHaveKeys works correctly', () => {
      expect({ a: 1, b: 2, c: 3 }).toHaveKeys(['a', 'b']);
      expect({ a: 1 }).not.toHaveKeys(['a', 'b', 'c']);
    });
  });
});
