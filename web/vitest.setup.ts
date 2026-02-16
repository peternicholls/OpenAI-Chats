import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, beforeAll, afterAll } from 'vitest'
import { server } from './__tests__/mocks/server'

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
