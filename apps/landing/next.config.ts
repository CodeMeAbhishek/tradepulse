import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  /** Cloud Run runs the standalone server, the same way apps/web does. */
  output: "standalone",
};

export default nextConfig;
