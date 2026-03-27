import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
    testDir: './__tests__/e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'html',
    use: {
        baseURL: 'http://localhost:3030',
        trace: 'on-first-retry',
    },
    projects: [
        {
            name: 'chrome',
            use: { ...devices['Desktop Chrome'], channel: 'chrome' },
        },
    ],
    webServer: [
        {
            command: 'npm run dev -- --webpack -p 3030',
            url: 'http://localhost:3030',
            reuseExistingServer: !process.env.CI,
            timeout: 120000,
        },
    ],
})
