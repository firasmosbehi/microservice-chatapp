import { defineConfig } from 'vite';

// Skip integration tests in CI environment since they require running services
const isInCI = process.env.CI === 'true' || process.env.GITHUB_ACTIONS === 'true';

export default defineConfig({
  test: {
    environment: 'node',
    setupFiles: ['./src/__integration-tests__/setup.integration.js'],
    globals: true,
    include: isInCI ? [] : ['src/__integration-tests__/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules/**', 'dist/**'],
    testTimeout: 15000,
    hookTimeout: 15000,
    teardownTimeout: 5000,
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