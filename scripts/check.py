#!/usr/bin/env python3
"""
Quick development checks - faster version of run-all.py for rapid feedback.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple


def run_quick_check(cmd: List[str], description: str) -> bool:
    """Run a quick check command."""
    print(f"🔍 {description}...", end=" ", flush=True)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30  # Quick timeout
        )
        
        if result.returncode == 0:
            print("✅")
            return True
        else:
            print("❌")
            error_lines = result.stderr.strip().split('\n')
            # Show just the first error line
            if error_lines and error_lines[0]:
                print(f"   → {error_lines[0]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ (timeout)")
        return False
    except FileNotFoundError:
        print("❌ (command not found)")
        return False
    except Exception as e:
        print(f"❌ ({e})")
        return False


def main():
    """Run quick development checks."""
    print("⚡ Quick Development Checks")
    print("-" * 30)
    
    start_time = time.time()
    
    # Quick checks (fast ones only)
    quick_checks = [
        (["python", "-c", "import src.nocodb_simple_client; print('OK')"], "Import check"),
        (["ruff", "check", "src/", "--select=F,E"], "Syntax check"), 
        (["black", "--check", "--fast", "src/"], "Format check"),
        (["mypy", "src/nocodb_simple_client/__init__.py"], "Type check (minimal)"),
        (["pytest", "-x", "--tb=no", "-q", "tests/", "-m", "not slow"], "Quick tests"),
    ]
    
    passed = 0
    total = len(quick_checks)
    
    for cmd, description in quick_checks:
        if run_quick_check(cmd, description):
            passed += 1
    
    duration = time.time() - start_time
    
    print("-" * 30)
    print(f"📊 {passed}/{total} checks passed ({duration:.1f}s)")
    
    if passed == total:
        print("🎉 Quick checks passed! Run 'python scripts/run-all.py' for full validation.")
        sys.exit(0)
    else:
        print("💥 Some quick checks failed. Fix issues or run 'python scripts/run-all.py' for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()