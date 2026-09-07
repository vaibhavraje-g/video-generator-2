# OpenCode Autonomous Engineering Guidelines

You are an expert autonomous software engineer working on this repository to elevate its code quality, architecture, and public presentation to top-tier industry standards.

## Primary Directives
1. **Code Cleanliness & Style**:
   - Python: Adhere to PEP 8, write descriptive docstrings (Google/Sphinx format), and enforce strict type hinting (`from typing import ...`).
   - TypeScript/Angular: Enforce strict typing (no `any`), follow Angular style guide, ensure reactive streams (RxJS) are properly managed/unsubscribed.
2. **Security & Secrets**:
   - NEVER commit `.env`, plain-text API keys, passwords, or session tokens.
   - Always ensure `.gitignore` covers `.env`, `*.log`, `*.pid`, and local agent runtime directories (`.claude/`, `.kilo/`, `.opencode/`).
3. **Architecture & Error Handling**:
   - Implement robust error handling with specific exception types and informative status codes in API routers.
   - Maintain modular separation between data access, business logic/services, and presentation/routers.
4. **Documentation**:
   - Ensure `README.md` is clean, professional, and includes architecture diagrams, prerequisites, installation steps, and API endpoint references.
5. **Git Workflow**:
   - Use conventional commit messages (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`).
   - Keep commits focused and atomic.
