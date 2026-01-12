export const RpcSchema = {
  wallet_connect: {
    Capabilities: {},
  },
};

export class Porto {
  static async create() {
    throw new Error('Porto connector is not available in this build.');
  }
}
