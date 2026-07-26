# Makefile for iac-engine Platform Governance

.PHONY: lint-security help

# Default target when calling make
help:
	@echo "========================================================="
	@echo "   Motor de IaC Centralizado (iac-engine) - Hub Makefile "
	@echo "========================================================="
	@echo "Available commands:"
	@echo "  make lint-security  - Run local security and backend-less configuration checks on Terraform files"
	@echo "  make help           - Display this help message"
	@echo "========================================================="

# Runs the security and backend-less lint checks using our custom python script
lint-security:
	@python3 scripts/lint_security.py .
