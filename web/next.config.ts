import type { NextConfig } from "next";
import path from 'path';

const nextConfig: NextConfig = {
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@/packages': path.resolve(__dirname, '../packages'),
    };
    return config;
  },
};

export default nextConfig;
