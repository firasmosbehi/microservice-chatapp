import { defineConfig } from 'vite';

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