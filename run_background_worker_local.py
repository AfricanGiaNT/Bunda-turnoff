#!/usr/bin/env python3
"""
Local runner for the Background Worker application.
This script helps test the Background Worker locally before deployment.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def setup_environment():
    """Setup environment variables for local testing."""
    # Set default environment variables if not already set
    env_vars = {
        'WORKER_PORT': '10000',
        'LOG_LEVEL': 'INFO',
        'EXPORT_DIR': '/tmp/exports',
        'STARTING_PETTY_CASH': '100000',
        'DAILY_SUMMARY_TIME_UTC': '15:00'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print("🔧 Environment setup complete")
    print(f"   WORKER_PORT: {os.environ.get('WORKER_PORT')}")
    print(f"   LOG_LEVEL: {os.environ.get('LOG_LEVEL')}")

def check_requirements():
    """Check if required packages are installed."""
    try:
        import requests
        print("✅ requests package available")
    except ImportError:
        print("❌ requests package not found")
        print("   Run: pip install requests")
        return False
    
    return True

def run_background_worker():
    """Run the Background Worker application."""
    print("🚀 Starting Background Worker...")
    print("=" * 50)
    
    try:
        # Run the Background Worker
        process = subprocess.Popen(
            [sys.executable, 'app_background_worker.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Background Worker: {e}")
        return None

def run_tests():
    """Run tests against the Background Worker."""
    print("\n🧪 Running tests...")
    print("-" * 30)
    
    try:
        result = subprocess.run(
            [sys.executable, 'test_background_worker.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def main():
    """Main function."""
    print("🤖 Background Worker Local Test Runner")
    print("=" * 50)
    
    # Check current directory
    if not Path('app_background_worker.py').exists():
        print("❌ app_background_worker.py not found in current directory")
        print("   Make sure you're in the project root directory")
        return 1
    
    # Setup environment
    setup_environment()
    
    # Check requirements
    if not check_requirements():
        return 1
    
    # Start Background Worker
    worker_process = run_background_worker()
    if not worker_process:
        return 1
    
    try:
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Check if process is still running
        if worker_process.poll() is not None:
            print("❌ Background Worker process exited early")
            stdout, stderr = worker_process.communicate()
            print("Output:", stdout)
            if stderr:
                print("Errors:", stderr)
            return 1
        
        print("✅ Background Worker started successfully")
        
        # Run tests
        tests_passed = run_tests()
        
        if tests_passed:
            print("\n✅ All tests passed!")
            print("🌐 Background Worker is ready for deployment")
        else:
            print("\n❌ Some tests failed")
            print("🔍 Check the output above for details")
        
        # Keep server running for manual testing
        print("\n" + "=" * 50)
        print("🔗 Server URLs:")
        print(f"   Root: http://localhost:10000/")
        print(f"   Health: http://localhost:10000/health")
        print(f"   Webhook: http://localhost:10000/telegram-webhook")
        print("\n⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Wait for user interrupt
        worker_process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 Stopping Background Worker...")
        worker_process.terminate()
        try:
            worker_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            worker_process.kill()
        print("✅ Background Worker stopped")
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        worker_process.terminate()
        return 1

if __name__ == "__main__":
    sys.exit(main())
