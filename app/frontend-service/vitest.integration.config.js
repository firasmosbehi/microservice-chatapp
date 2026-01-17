import { defineConfig } from 'vite';

// Check if we can connect to the gateway service
const isGatewayAvailable = async () => {
  try {
    const response = await fetch('http://localhost:8000/health', { timeout: 5000 });
    return response.ok;
  } catch (error) {
    return false;
  }
};

export default defineConfig({
  test: {
    environment: 'node',
    setupFiles: ['./src/__integration-tests__/setup.integration.js'],
    globals: true,
    include: ['src/__integration-tests__/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules/**', 'dist/**'],
    testTimeout: 30000,
    hookTimeout: 30000,
    teardownTimeout: 10000,
    reporters: ['verbose'],
    coverage: {
      enabled: true,
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**'],
      exclude: ['src/__tests__/**', 'src/__integration-tests__/**', 'src/setupTests.js']
    }
  },
});