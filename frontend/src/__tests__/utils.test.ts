import { cn, formatAddress, formatTokenAmount, generateId } from '../lib/utils';

describe('utils', () => {
  beforeAll(() => {
    if (!global.crypto) {
      global.crypto = {
        randomUUID: () => 'test-id',
      } as Crypto;
    }
  });

  it('merges class names', () => {
    expect(cn('a', false && 'b', 'c')).toBe('a c');
  });

  it('formats address', () => {
    expect(formatAddress('0x1234567890abcdef', 4)).toBe('0x1234...cdef');
  });

  it('formats token amount', () => {
    expect(formatTokenAmount(1000000000000000000n, 18)).toBe('1');
  });

  it('generates an id', () => {
    const id = generateId();
    expect(id).toBeTruthy();
  });
});
