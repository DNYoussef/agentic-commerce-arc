const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      porto: path.resolve(__dirname, 'src/porto'),
      'porto/internal': path.resolve(__dirname, 'src/porto/internal'),
    };

    // Client-side fallbacks for Node.js and React Native modules
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        // React Native modules (MetaMask SDK)
        '@react-native-async-storage/async-storage': false,
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
