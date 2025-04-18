#!/bin/bash

set -e

pytest

cd frontend && CI=true yarn test && cd ..
