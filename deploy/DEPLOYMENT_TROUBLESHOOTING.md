# Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. "uvicorn: command not found" Error

This error occurs when the Python dependencies are not properly installed. Here are the solutions:

#### Solution A: Use main.py (Recommended)
```yaml
startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Solution B: Use app.py
```yaml
startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
```

#### Solution C: Use wsgi.py
```yaml
startCommand: uvicorn wsgi:app --host 0.0.0.0 --port $PORT
```

### 2. Alternative Entry Points

We've created multiple entry point files to ensure compatibility:

- **main.py** - Primary entry point with full FastAPI app
- **app.py** - Alternative entry point (some platforms look for this)
- **wsgi.py** - WSGI-compatible entry point
- **Procfile** - Heroku-style deployment file

### 3. Build Commands

The current build command includes debugging information:
```yaml
buildCommand: |
  python --version
  pip --version
  pip install --upgrade pip
  pip install -r requirements.txt
  pip list
```

### 4. Python Version

Using Python 3.11.0 for better compatibility with Render.

### 5. Dependency Management

- **requirements.txt** - Minimal version constraints for better compatibility
- **runtime.txt** - Specifies Python version

## Testing Locally

Before deploying, test locally:

```bash
# Test main.py
python -c "from main import app; print('✅ main.py works')"

# Test uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Test app.py
python -c "from app import app; print('✅ app.py works')"

# Test wsgi.py
python -c "from wsgi import app; print('✅ wsgi.py works')"
```

## Render-Specific Issues

1. **Environment Variables**: Ensure all required env vars are set in Render dashboard
2. **Build Timeout**: Free tier has limited build time, keep dependencies minimal
3. **Python Path**: Render should automatically detect Python environment

## Fallback Commands

If uvicorn still fails, try these alternatives:

```yaml
# Alternative 1: Use Python directly
startCommand: python -m uvicorn main:app --host 0.0.0.0 --port $PORT

# Alternative 2: Use gunicorn (if available)
startCommand: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT

# Alternative 3: Use Python with explicit module path
startCommand: python -c "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=int('$PORT'))"
```

## Debugging Steps

1. Check build logs for Python/pip version information
2. Verify all dependencies are installed (`pip list` output)
3. Test entry point imports locally
4. Check for syntax errors in Python files
5. Verify environment variables are set correctly
