import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
    plugins: [react()],
    test: {
        environment: 'jsdom',
        environmentOptions: {
            jsdom: {
                url: 'http://localhost',
            },
        },
        setupFiles: ['./vitest.setup.ts'],
        include: ['**/__tests__/**/*.{test,spec}.{ts,tsx}', '**/*.{test,spec}.{ts,tsx}'],
        exclude: ['**/node_modules/**', '**/e2e/**'],
        globals: true,
        css: true,
        typecheck: {
            tsconfig: './tsconfig.test.json',
        },
        coverage: {
            provider: 'v8',
            reporter: ['text', 'json', 'html'],
            exclude: [
                'node_modules/',
                '__tests__/',
                '**/*.d.ts',
                '**/*.config.*',
                'playwright.config.ts',
                '.next/',
                '.next/**',
            ],
        },
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
})
