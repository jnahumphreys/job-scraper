# Setting up GitHub Actions with Coverage Reporting

This project is configured with GitHub Actions that automatically run tests on every pull request to the main branch, with comprehensive coverage reporting.

## What's Included

### GitHub Actions Workflow (`.github/workflows/test.yml`)

- **Multi-Python Testing**: Tests against Python 3.10, 3.11, and 3.12
- **Coverage Reporting**: Generates XML, HTML, and terminal coverage reports
- **Codecov Integration**: Uploads coverage reports to Codecov (optional)
- **PR Comments**: Automatically adds coverage reports to pull request comments
- **Artifacts**: Saves HTML coverage reports as downloadable artifacts

### Coverage Configuration (`.codecov.yml`)

- Customized coverage thresholds and settings
- Ignores test files and cache directories
- Configures PR comment layout and behavior

## Setting up Codecov (Optional)

To enable coverage reporting to Codecov:

1. **Sign up at Codecov**
   - Go to [codecov.io](https://codecov.io)
   - Sign in with your GitHub account
   - Add your repository

2. **Get your Codecov token**
   - In your Codecov repository settings, copy the upload token

3. **Add the token to GitHub Secrets**
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: Your Codecov upload token

4. **Push changes**
   - The workflow will automatically upload coverage reports on the next test run

## Running Tests Locally

Use the provided script for local testing:

```bash
./run_tests.sh
```

This will:
- Run all tests with coverage
- Generate XML, HTML, and terminal reports
- Display coverage statistics
- Create an HTML report you can open in your browser

## GitHub Actions Features

### Trigger Conditions
- All pull requests targeting the `main` branch
- Direct pushes to the `main` branch

### Test Matrix
- Tests run on Ubuntu latest
- Python versions: 3.10, 3.11, 3.12
- Tests continue even if one Python version fails

### Coverage Features
- **XML Report**: For Codecov and other tools
- **HTML Report**: Saved as downloadable artifact (Python 3.12 only)
- **Terminal Report**: Shows missing lines during CI
- **PR Comments**: Automatic coverage comments on pull requests

### Caching
- pip dependencies are cached for faster builds
- Cache is based on `requirements.txt` content

## Viewing Coverage Reports

### During CI
- Check the Actions tab for test results
- Download HTML coverage artifact from successful runs
- View coverage comments on pull requests

### Locally
- Run `./run_tests.sh`
- Open `htmlcov/index.html` in your browser
- Check terminal output for quick overview

## Coverage Thresholds

Current configuration:
- **Project Coverage**: 80% target (with 1% threshold)
- **Patch Coverage**: 80% target for new code
- **Color Coding**: 70% (orange) to 90% (green)

## Troubleshooting

### Tests fail locally but work in CI
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility
- Verify PYTHONPATH is set correctly

### Coverage reports not uploading
- Verify `CODECOV_TOKEN` is set in GitHub Secrets
- Check that coverage.xml is being generated
- Review GitHub Actions logs for error messages

### PR comments not appearing
- Ensure the PR comment action has proper permissions
- Check that the coverage job completed successfully
- Verify the workflow has access to GitHub token