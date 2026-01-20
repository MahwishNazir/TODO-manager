import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
};

export default nextConfig;
