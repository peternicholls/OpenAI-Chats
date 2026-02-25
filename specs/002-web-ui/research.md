# Research: Web UI Technology Choices

**Feature**: 002-web-ui  
**Date**: 2026-02-12  
**Purpose**: Resolve NEEDS CLARIFICATION items from Technical Context

## Overview

This document consolidates research findings for technology choices needed to build a beautiful, consistent web UI with Docker deployment for the ChatGPT Archive tool.

---

## Research Areas

### 1. Frontend Framework

**Decision**: **Next.js (React framework)**

**Rationale**:
- **Full-stack React framework** with built-in routing, API routes (could host FastAPI alternative if needed), and SSR/SSG capabilities
- **File-based routing** reduces boilerplate and improves developer experience
- **Large ecosystem** of component libraries and tooling
- **Production-ready** with excellent TypeScript support
- **Image and asset optimization** built-in
- **Active development** and strong community support (Vercel backing)
- **Better for SEO** if future discoverability is desired

**Alternatives Considered**:
- **Vue/Nuxt**: Excellent, but Next.js has slightly larger ecosystem and more enterprise adoption
- **Svelte/SvelteKit**: More performant and simpler, but smaller ecosystem and fewer component libraries
- **Plain React (Vite)**: More manual setup required for routing, SSR, build optimization
- **Solid.js**: Very performant but too new, smaller ecosystem

**Why Next.js chosen over alternatives**:
- Built-in TypeScript support (first-class)
- App Router provides modern React patterns (Server Components, Suspense)
- Simpler deployment with containerization
- Best balance of ecosystem maturity and modern features

---

### 2. Component Library / Design System

**Decision**: **shadcn/ui + Tailwind CSS**

**Rationale**:
- **shadcn/ui** is not a traditional component library—it's a collection of **copy-paste-able, customizable components** built on Radix UI primitives
- **Full design control**: Components are added to your codebase, not imported as dependencies
- **Tailwind CSS integration**: Utility-first CSS for rapid, consistent styling
- **Accessibility built-in**: Uses Radix UI primitives (WAI-ARIA compliant)
- **Modern, beautiful defaults**: Clean design that can be themed
- **No bundle bloat**: Only include components you use

**Alternatives Considered**:
- **Material-UI (MUI)**: Feature-rich but heavy bundle size, harder to customize deeply
- **Ant Design**: Enterprise-focused, but opinionated design that's harder to override
- **Chakra UI**: Great DX but adds bundle weight and is component-library-as-dependency
- **Mantine**: Modern and feature-rich, but newer and smaller community
- **Headless UI + custom styles**: More work to build consistent design from scratch

**Why shadcn/ui + Tailwind chosen**:
- **"Beautiful, consistent UX and design"** requirement satisfied by cohesive design tokens
- **Framework technology for consistency** requirement: Tailwind's utility classes + shadcn components provide the framework
- Lightweight and performant (no runtime JS overhead from CSS-in-JS)
- Easy customization without fighting the library
- Excellent TypeScript support

---

### 3. Frontend Testing Framework

**Decision**: **Vitest + React Testing Library**

**Rationale**:
- **Vitest**: Fast, Vite-native test runner (works seamlessly with Next.js + Vite)
  - Compatible with Jest API (easy migration if needed)
  - Much faster than Jest (ESM-first, Vite-powered)
  - Built-in TypeScript support
  - Better dev experience with HMR for tests
- **React Testing Library**: Industry standard for testing React components
  - Focuses on user behavior over implementation details
  - Encourages accessible markup
  - Works with any test runner

**Alternatives Considered**:
- **Jest + React Testing Library**: Standard choice but slower, requires more configuration
- **Playwright Component Testing**: Too new, less mature than RTL

**Why Vitest chosen**:
- Faster test execution (important for CI/CD)
- Better integration with modern Vite/Next.js tooling
- Negligible migration risk (Jest-compatible API)

---

### 4. End-to-End Testing Framework

**Decision**: **Playwright**

**Rationale**:
- **Cross-browser testing**: Chromium, Firefox, WebKit (Safari) support
- **Modern API**: Async/await, auto-waiting, better debugging
- **Built-in test runner**: No need for separate runner like Jest
- **Trace viewer**: Excellent debugging tools with screenshots, network logs
- **Microsoft-backed**: Active development and enterprise support
- **Codegen**: Can record user interactions to generate tests

**Alternatives Considered**:
- **Cypress**: Popular but has architectural limitations (no multi-tab, no true cross-browser until recently)
- **Selenium**: Legacy, slower, more complex setup

**Why Playwright chosen**:
- Better developer experience (API design, debugging tools)
- True cross-browser support (Cypress only recently added this)
- Faster and more reliable (auto-waits, better retry logic)
- Better Docker/CI integration

---

## Backend API Technology

**Decision**: **FastAPI**

**Rationale**:
- **Already listed in Technical Context** (not a NEEDS CLARIFICATION)
- Perfect fit for wrapping existing `chatgpt_archive` Python library
- **Automatic OpenAPI docs** generation (Swagger UI)
- **Type safety** with Pydantic models
- **Async support** for better concurrency
- **Fast** (Starlette + Uvicorn)

**No alternatives needed**: FastAPI is the obvious choice for a Python REST API in 2026.

---

## Docker & Deployment Strategy

**Decision**: **Multi-stage Docker builds + Docker Compose**

**Rationale**:
- **Multi-stage builds** keep images small:
  - Frontend: Build with Node, serve with nginx (static export from Next.js)
  - Backend: Python slim image with only runtime dependencies
- **Docker Compose** orchestrates both services + volume for SQLite DB
- **nginx** can serve frontend and reverse proxy API requests
- **Single `docker-compose up`** deploys entire stack

**Structure**:
```yaml
services:
  web:
    build: ./docker/web.Dockerfile
    ports: ["3000:80"]
    depends_on: [api]
  
  api:
    build: ./docker/api.Dockerfile
    ports: ["8000:8000"]
    volumes:
      - archive-data:/data  # SQLite database persistence
    environment:
      - CHATGPT_ARCHIVE_DB=/data/chats.db
```

**Alternatives Considered**:
- **Single container**: Harder to scale and maintain, mixing concerns
- **Kubernetes**: Overkill for single-user deployment requirement

---

## Technology Stack Summary

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend Framework** | Next.js 14+ (App Router) | Modern React with optimal DX, SSR, routing |
| **UI Components** | shadcn/ui + Tailwind CSS | Beautiful, customizable, accessible, consistent |
| **Frontend Language** | TypeScript 5+ | Type safety, excellent tooling |
| **State Management** | React Server Components + React Query (TanStack Query) | Optimal data fetching, minimal client state |
| **API Client** | fetch (native) + React Query | Type-safe API calls, caching, automatic refetch |
| **Unit Testing** | Vitest + React Testing Library | Fast, modern, Jest-compatible |
| **E2E Testing** | Playwright | Best-in-class DX, cross-browser, debugging |
| **Backend API** | FastAPI + Uvicorn | Python async REST API, auto-docs |
| **API Models** | Pydantic V2 | Type-safe request/response validation |
| **Container Runtime** | Docker + Docker Compose | Standard, portable, user-requested |
| **Web Server** | nginx (for static frontend) | Production-proven, lightweight |

---

## Development Workflow

1. **Local Development**:
   - Backend: `cd api && uvicorn main:app --reload`
   - Frontend: `cd web && npm run dev`
   - Full stack: `docker-compose -f docker-compose.dev.yml up`

2. **Testing**:
   - Frontend unit: `cd web && npm test`
   - E2E: `cd web && npm run test:e2e`
   - Backend: `pytest` (existing)

3. **Production Build**:
   - `docker-compose build`
   - `docker-compose up -d`

---

## Open Questions / Future Considerations

- **Authentication**: Not required for MVP (single-user deployment), but could add basic auth via nginx or API middleware
- **WebSocket/SSE**: For real-time import progress? (Could start with polling, upgrade to SSE if needed)
- **Mobile responsiveness**: Should be included from start via Tailwind responsive utilities
- **Dark mode**: Easy to add with Tailwind and Next.js (could be Phase 2 enhancement)

---

## Conclusion

All NEEDS CLARIFICATION items have been resolved with well-justified technology choices that satisfy the requirements:
- ✅ Beautiful, consistent UX (shadcn/ui + Tailwind)
- ✅ Framework for consistency (Next.js + design system)
- ✅ Docker deployment (Docker Compose)
- ✅ All feature 001 functions (FastAPI wraps existing library)
- ✅ Modern, maintainable stack (TypeScript, React, FastAPI)
