const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  webpack: (config, { isServer }) => {
    // Alias React Native modules to stubs (works for both server/client)
    config.resolve.alias = {
      ...config.resolve.alias,
      porto: path.resolve(__dirname, 'src/porto'),
      'porto/internal': path.resolve(__dirname, 'src/porto/internal'),
      // Stub React Native async-storage (required by MetaMask SDK)
      '@react-native-async-storage/async-storage': path.resolve(
        __dirname,
        'src/stubs/async-storage.js'
      ),
    };

    // Client-side fallbacks for Node.js modules
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        // Node.js modules (WalletConnect, pino)
        fs: false,
        net: false,
        tls: false,
        crypto: false,
        stream: false,
        url: false,
        zlib: false,
        http: false,
        https: false,
        assert: false,
        os: false,
        path: false,
        // Pino logging
        'pino-pretty': false,
      };
    }

    return config;
  },
};

module.exports = nextConfig;
