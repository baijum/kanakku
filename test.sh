#!/bin/bash

set -e

pytest

cd frontend && CI=true yarn test && cd ..
cd tools/ledgertransactions && go test -v ./... && cd ../..
cd tools/accountimporter && cargo test -- --test-threads=1 && cd ../..