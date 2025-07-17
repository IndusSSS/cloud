# Contributing

How to contribute to the SmartSecurity Cloud platform.

## Quick Start

### Setup
```bash
# Clone and setup
git clone https://github.com/your-org/smartsecurity-cloud.git
cd smartsecurity-cloud
poetry install && poetry shell
docker compose up -d
```

### Development Workflow
1. **Create branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Follow the [MESS Guidelines](./MESS_GUIDELINES.md)
3. **Test**: `poetry run pytest`
4. **Commit**: `git commit -m "feat: add your feature"`
5. **Push**: `git push origin feature/your-feature`
6. **Create PR**: Open pull request on GitHub

## Branch Naming

```
feature/SS-123-add-user-authentication
bugfix/SS-456-fix-login-validation
hotfix/SS-789-critical-security-patch
```

## Commit Messages

```
feat: add user authentication
fix: resolve login validation issue
docs: update API documentation
style: format code with black
```

## Before Submitting

- [ ] Code follows [MESS Guidelines](./MESS_GUIDELINES.md)
- [ ] Tests pass: `poetry run pytest`
- [ ] Code formatted: `poetry run black .`
- [ ] No linting errors: `poetry run ruff check`

## That's It!

Focus on building great features. The team will help with the rest. 