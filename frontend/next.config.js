/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  transpilePackages: ['@neo4j-nvl/react', '@neo4j-nvl/base'],
  experimental: {
    optimizePackageImports: ['@chakra-ui/react'],
  },
  // async rewrites() {
  //   return [
  //     {
  //       source: '/api/:path*',
  //       destination: `http://context-graphs.innovationlab:8081/api/:path*`,
  //     },
  //   ];
  // },
};

module.exports = nextConfig;
