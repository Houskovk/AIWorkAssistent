import os
import sys
import subprocess

def main():
    """
    Entry point for the application.
    Runs the Streamlit frontend.
    """
    environment = os.environ.copy()
    
    # Add project root to PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    environment["PYTHONPATH"] = project_root
    
    try:
        from streamlit.web import cli as stcli
    except ImportError:
        # Fallback if streamlit is not installed (should not happen if requirements met)
        print("Streamlit not found. Please install requirements.txt")
        return

    sys.argv = ["streamlit", "run", os.path.join(project_root, "app", "frontend", "ui.py")]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()

