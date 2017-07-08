"""
Allow easy use of cross-platform relative file paths.
"""
import os

# Module is initialized
initialized = False

# Global root directory of project
directory = None

def init(project_dir):
    """Initialize the module by setting the root directory of the project."""
    global initialized, directory
    initialized = True
    # Redirect project directory to ./Application/Contents/Resources if is an app
    if 'python' in project_dir:
        directory = os.path.dirname(os.path.dirname(project_dir))
    else:
        directory = project_dir

def path(*args):
    if not initialized:
        raise AttributeError('module not initialized')
    return os.path.join(directory, *args)
