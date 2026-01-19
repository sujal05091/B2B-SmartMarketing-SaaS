/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Add this line for static export
  images: {
    unoptimized: true,  // Required for static export
    domains: ['localhost', 'lh3.googleusercontent.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXTAUTH_URL: process.env.NEXTAUTH_URL || 'http://localhost:3000',
  },
}

module.exports = nextConfig