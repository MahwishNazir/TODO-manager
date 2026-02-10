import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  // Fix workspace root detection issue
  turbopack: {
    root: path.resolve(__dirname),
  },

  // Performance optimizations
  compress: true,

  // Image optimization
  images: {
    formats: ["image/avif", "image/webp"],
    minimumCacheTTL: 60,
  },

  // Enable React strict mode for better debugging
  reactStrictMode: true,

  // Optimize package imports to reduce bundle size
  experimental: {
    optimizePackageImports: [
      "lucide-react",
      "@radix-ui/react-dialog",
      "@radix-ui/react-dropdown-menu",
      "@radix-ui/react-checkbox",
      "@radix-ui/react-alert-dialog",
      "@radix-ui/react-label",
      "@radix-ui/react-slot",
    ],
  },

  // Production source maps disabled for smaller bundles
  productionBrowserSourceMaps: false,

  // Proxy backend API requests to eliminate CORS issues
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [
      {
        // Proxy task API routes to the FastAPI backend
        // Matches /api/{userId}/tasks and /api/{userId}/tasks/{taskId}/*
        source: "/api/:userId((?!auth|token|chatkit)[^/]+)/tasks/:path*",
        destination: `${backendUrl}/api/:userId/tasks/:path*`,
      },
      {
        // Proxy task API routes (no sub-path)
        source: "/api/:userId((?!auth|token|chatkit)[^/]+)/tasks",
        destination: `${backendUrl}/api/:userId/tasks`,
      },
      {
        // Proxy health check
        source: "/api/health",
        destination: `${backendUrl}/health`,
      },
    ];
  },
};

export default nextConfig;
