#!/bin/bash

echo "Running Black formatting check..."
black . --check

echo -e "\nRunning flake8..."
flake8 .

echo -e "\nRunning tests with coverage..."
pytest

echo -e "\nCoverage report generated in htmlcov/index.html" 