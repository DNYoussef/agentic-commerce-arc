const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      porto: path.resolve(__dirname, 'src/porto'),
      'porto/internal': path.resolve(__dirname, 'src/porto/internal'),
    };
    // Add fallbacks for React Native modules used by MetaMask SDK
    config.resolve.fallback = {
      ...config.resolve.fallback,
      '@react-native-async-storage/async-storage': false,
    };
    return config;
  },
};

module.exports = nextConfig;
