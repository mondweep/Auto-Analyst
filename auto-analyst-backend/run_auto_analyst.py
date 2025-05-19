#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import re
from pathlib import Path

# Add compatibility message
def print_banner():
    print("=" * 80)
    print("Auto-Analyst Backend Runner".center(80))
    print("=" * 80)
    print("This script helps run the Auto-Analyst backend with NumPy compatibility fixes")
    print("and enhanced attribute-specific filtering capabilities.")
    print("-" * 80)

def ensure_virtual_env():
    """Ensure we're running in an appropriate virtual environment"""
    if 'VIRTUAL_ENV' not in os.environ:
        print("⚠️ Warning: Not running in a virtual environment.")
        print("It's recommended to activate a virtual environment before running this script.")
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            print("Exiting. Please activate a virtual environment and try again.")
            sys.exit(1)

def check_numpy_compatibility():
    """Check NumPy version and ensure compatibility"""
    try:
        import numpy as np
        numpy_version = np.__version__
        print(f"✅ NumPy version: {numpy_version}")
        
        major_version = int(numpy_version.split('.')[0])
        if major_version >= 2:
            print("⚠️ Warning: Running with NumPy 2.x. Some libraries may expect NumPy 1.x API.")
            print("Adding compatibility flags...")
            
            # Set environment variable for NumPy 1.x compatibility mode
            os.environ['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION_ENABLED'] = '1'
            os.environ['NUMPY_EXPERIMENTAL_DTYPE_API'] = '1'
            
            print("✅ NumPy compatibility flags set.")
        else:
            print("✅ NumPy 1.x detected, no compatibility flags needed.")
    except ImportError:
        print("❌ NumPy not installed. Please install with: pip install numpy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error checking NumPy version: {str(e)}")
        sys.exit(1)

def check_attribute_query_support():
    """Check and enhance attribute query support"""
    try:
        # Check if direct_count_query.py exists
        utils_dir = Path("src/utils")
        direct_count_path = utils_dir / "direct_count_query.py"
        
        if not utils_dir.exists():
            utils_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {utils_dir}")
        
        if not direct_count_path.exists():
            # Copy from root if it exists there
            root_count_path = Path("direct_count_query.py")
            if root_count_path.exists():
                import shutil
                shutil.copy(root_count_path, direct_count_path)
                print(f"✅ Copied direct_count_query.py to {direct_count_path}")
            else:
                print("⚠️ Warning: direct_count_query.py not found.")
                print("Attribute-specific filtering capabilities may be limited.")
        else:
            print(f"✅ Found attribute query support at {direct_count_path}")
            
        # Check if we have access to the vehicles dataset
        found_dataset = False
        possible_paths = [
            "exports/vehicles.csv",
            "data/vehicles.csv",
            "../exports/vehicles.csv",
            "../data/vehicles.csv"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                print(f"✅ Found vehicles dataset at: {path}")
                found_dataset = True
                break
                
        if not found_dataset:
            print("⚠️ Warning: vehicles.csv not found in standard locations.")
            print("Make sure the dataset is available for attribute filtering to work properly.")
        
    except Exception as e:
        print(f"❌ Error checking attribute query support: {str(e)}")

def run_backend(port=8000, debug=True):
    """Run the backend server"""
    try:
        print(f"Starting Auto-Analyst backend on port {port}...")
        
        # Prepare the command
        cmd = [sys.executable, "app.py"]
        if port != 8000:
            cmd.extend(["--port", str(port)])
        if debug:
            cmd.append("--debug")
            
        # Set environment variable for NumPy 1.x compatibility mode if using NumPy 2.x
        try:
            import numpy as np
            major_version = int(np.__version__.split('.')[0])
            if major_version >= 2:
                env = os.environ.copy()
                env['NUMPY_EXPERIMENTAL_ARRAY_FUNCTION_ENABLED'] = '1'
                env['NUMPY_EXPERIMENTAL_DTYPE_API'] = '1'
                subprocess.run(cmd, env=env)
            else:
                subprocess.run(cmd)
        except ImportError:
            # If numpy not available, just try to run
            subprocess.run(cmd)
            
    except KeyboardInterrupt:
        print("\nStopping backend server...")
    except Exception as e:
        print(f"❌ Error running backend: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Run Auto-Analyst backend with enhanced compatibility")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--skip-checks", action="store_true", help="Skip compatibility checks")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug mode")
    
    args = parser.parse_args()
    
    print_banner()
    
    if not args.skip_checks:
        ensure_virtual_env()
        check_numpy_compatibility()
        check_attribute_query_support()
    
    run_backend(port=args.port, debug=not args.no_debug)

if __name__ == "__main__":
    main() 