#!/usr/bin/env python3
"""
AutoForge Live Dashboard Entry Point

This script launches the AutoForge Live Vehicle Dashboard, a real-time
visualization system that demonstrates vehicle health monitoring capabilities.

Usage:
    python run_dashboard.py

Requirements:
    - streamlit
    - plotly
    - pandas
    - numpy

The dashboard will be available at http://localhost:8501
"""

import sys
import subprocess
import importlib.util
import os


def check_streamlit_installed():
    """
    Check if streamlit is installed using importlib.
    
    Returns:
        bool: True if streamlit is installed, False otherwise
    """
    spec = importlib.util.find_spec("streamlit")
    return spec is not None


def print_installation_instructions():
    """Print installation instructions for missing dependencies."""
    print("\n" + "="*70)
    print("❌ Missing Dependencies")
    print("="*70)
    print("\nStreamlit is not installed. Please install the required dependencies:")
    print("\n  pip install -r requirements.txt")
    print("\nOr install streamlit directly:")
    print("\n  pip install streamlit plotly pandas numpy")
    print("\n" + "="*70 + "\n")


def print_usage_instructions():
    """Print usage instructions before launching the dashboard."""
    print("\n" + "="*70)
    print("🚀 AutoForge Live Vehicle Dashboard")
    print("="*70)
    print("\nLaunching real-time vehicle health monitoring dashboard...")
    print("\nFeatures:")
    print("  • Real-time VSS signal simulation")
    print("  • Interactive fault scenario injection")
    print("  • Live gauges and trend charts")
    print("  • Alert monitoring and history")
    print("\nThe dashboard will open in your browser at:")
    print("  http://localhost:8501")
    print("\nPress Ctrl+C to stop the dashboard.")
    print("="*70 + "\n")


def check_app_file_exists():
    """
    Check if the dashboard app.py file exists.
    
    Returns:
        bool: True if app.py exists, False otherwise
    """
    app_path = os.path.join("autoforge", "dashboard", "app.py")
    return os.path.isfile(app_path)


def main():
    """Main entry point for the dashboard launcher."""
    # Check if streamlit is installed
    if not check_streamlit_installed():
        print_installation_instructions()
        sys.exit(1)
    
    # Check if the dashboard app file exists
    if not check_app_file_exists():
        print("\n" + "="*70)
        print("❌ File Not Found")
        print("="*70)
        print("\nThe dashboard application file was not found:")
        print("  autoforge/dashboard/app.py")
        print("\nPlease ensure you are running this script from the project root directory.")
        print("="*70 + "\n")
        sys.exit(1)
    
    # Print usage instructions
    print_usage_instructions()
    
    # Launch the dashboard using streamlit
    try:
        subprocess.run(
            ["streamlit", "run", "autoforge/dashboard/app.py"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching dashboard: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Goodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
