import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      { source: "/queue", destination: "/workbench/queue", permanent: false },
      { source: "/cases/new", destination: "/workbench/cases/new", permanent: false },
      { source: "/cases/:id", destination: "/workbench/cases/:id", permanent: false },
      { source: "/approvals", destination: "/workbench/approvals", permanent: false },
      { source: "/regwatch", destination: "/workbench/regwatch", permanent: false },
    ];
  },
};

export default nextConfig;
