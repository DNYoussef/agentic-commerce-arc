const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      porto: path.resolve(__dirname, 'src/porto'),
      'porto/internal': path.resolve(__dirname, 'src/porto/internal'),
    };
    return config;
  },
};

module.exports = nextConfig;
