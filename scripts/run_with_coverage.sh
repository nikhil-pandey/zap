#!/bin/bash

# Run tests with coverage
pytest --cov=zap.templating --cov-report=html:coverage_report --cov-report=term tests/templating