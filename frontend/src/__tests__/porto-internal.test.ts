import { z } from '../porto/internal';

describe('porto internal', () => {
  it('exports rpc schema', () => {
    expect(z).toBeDefined();
  });
});
