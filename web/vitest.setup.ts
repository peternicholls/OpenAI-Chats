import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, beforeAll, afterAll } from 'vitest'
import { server } from './__tests__/mocks/server'

// Polyfill ResizeObserver for Radix UI components (e.g. Tooltip) in jsdom
if (typeof ResizeObserver === 'undefined') {
    global.ResizeObserver = class ResizeObserver {
        observe() { }
        unobserve() { }
        disconnect() { }
    }
}

// Cleanup after each test
afterEach(() => {
    cleanup()
})

// Start MSW server before all tests
beforeAll(() => {
    server.listen({ onUnhandledRequest: 'warn' })
})

// Reset handlers after each test
afterEach(() => {
    server.resetHandlers()
})

// Stop server after all tests
afterAll(() => {
    server.close()
})
