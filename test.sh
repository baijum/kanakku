#!/bin/bash

set -e

# Start total timer
TOTAL_START=$(date +%s)

echo "🧪 Running all test suites..."
echo "================================"

# Python tests
echo "📋 Running Python tests..."
PYTHON_START=$(date +%s)
pytest
PYTHON_END=$(date +%s)
PYTHON_TIME=$((PYTHON_END - PYTHON_START))
echo "✅ Python tests completed in ${PYTHON_TIME}s"
echo ""

# Frontend tests
echo "⚛️  Running Frontend tests..."
FRONTEND_START=$(date +%s)
cd frontend && CI=true yarn test && cd ..
FRONTEND_END=$(date +%s)
FRONTEND_TIME=$((FRONTEND_END - FRONTEND_START))
echo "✅ Frontend tests completed in ${FRONTEND_TIME}s"
echo ""

# Go tests
echo "🐹 Running Go tests..."
GO_START=$(date +%s)
cd tools/ledgertransactions && go test -v ./... && cd ../..
GO_END=$(date +%s)
GO_TIME=$((GO_END - GO_START))
echo "✅ Go tests completed in ${GO_TIME}s"
echo ""

# Rust tests
echo "🦀 Running Rust tests..."
RUST_START=$(date +%s)
cd tools/accountimporter && cargo test -- --test-threads=1 && cd ../..
RUST_END=$(date +%s)
RUST_TIME=$((RUST_END - RUST_START))
echo "✅ Rust tests completed in ${RUST_TIME}s"
echo ""

# Calculate and display total time
TOTAL_END=$(date +%s)
TOTAL_TIME=$((TOTAL_END - TOTAL_START))

echo "================================"
echo "📊 Test Summary:"
echo "  Python:   ${PYTHON_TIME}s"
echo "  Frontend: ${FRONTEND_TIME}s"
echo "  Go:       ${GO_TIME}s"
echo "  Rust:     ${RUST_TIME}s"
echo "--------------------------------"
echo "  Total:    ${TOTAL_TIME}s"
echo "================================"
echo "🎉 All tests passed!"