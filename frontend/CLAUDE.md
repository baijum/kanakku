# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Start development server: `npm start`
- Build for production: `npm run build`
- Run all tests: `npm test`
- Run a single test: `npm test -- --testMatch="**/fileName.test.jsx"`
- Eject from Create React App: `npm run eject`

## Code Style
- React functional components with hooks
- JSX files use .jsx extension
- Standard eslint config (extends react-app, react-app/jest)
- Material-UI (MUI) for UI components
- Use axios for API calls, via the configured axiosInstance
- Prefer async/await for asynchronous code
- Import order: React, MUI, other external libraries, internal components
- Exception handling with try/catch blocks with console.error for logging
- State management via React hooks (useState, useEffect)
- React Router v6 for routing with component-based routes