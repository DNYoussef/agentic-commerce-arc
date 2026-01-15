import { Porto, RpcSchema } from '../porto';

describe('porto', () => {
  it('exposes wallet_connect capability', () => {
    expect(RpcSchema.wallet_connect).toBeDefined();
  });

  it('throws on create', async () => {
    await expect(Porto.create()).rejects.toThrow('Porto connector is not available in this build.');
  });
});
