import subprocess
import tempfile
import os
from pathlib import Path
import shutil
import sys
import re

class DependencyManager:
    """Manages dependencies required for Manim"""
    
    @staticmethod
    def install_dependencies():
        """Install required dependencies with specific versions"""
        dependencies = [
            "numpy==1.23.5",
            "scipy==1.9.3",
            "manim==0.17.3",
            "pillow>=7.2.0",
            "pycairo>=1.19.1",
            "manimpango>=0.2.4",
            "networkx>=2.5",
            "decorator==5.1.1",
            "sympy==1.10.1"
        ]
        
        for dep in dependencies:
            try:
                subprocess.check_call([
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--no-cache-dir",
                    dep
                ])
            except subprocess.CalledProcessError as e:
                print(f"Error installing {dep}: {e}")
                return False
        return True