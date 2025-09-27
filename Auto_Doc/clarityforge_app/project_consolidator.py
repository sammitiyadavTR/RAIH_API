import os
from rich.tree import Tree
from rich.console import Console
from rich import print
from rich.prompt import Confirm
from colorama import Fore, init
import inquirer
import pathspec
import mimetypes

from .handlers.userinterface import UserInterface

def get_gitignore_spec(root_dir):
    gitignore_path = os.path.join(root_dir, '.gitignore')
    patterns = ['.git']
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            spec = pathspec.PathSpec.from_lines('gitwildmatch', 
                                              patterns + [line.rstrip() for line in f])
            return spec
    else:
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
def get_cfignore_spec(root_dir):
    cfignore_path = os.path.join(root_dir, '.cfignore')  
    if os.path.exists(cfignore_path):
        with open(cfignore_path, 'r', encoding='utf-8') as f:
            spec = pathspec.PathSpec.from_lines('gitwildmatch', 
                                              [line.rstrip() for line in f])
            return spec
    else:
        return None
    
def get_cfinclude_spec(root_dir):
    cfinclude_path = os.path.join(root_dir, '.cfinclude')  
    if os.path.exists(cfinclude_path):
        with open(cfinclude_path, 'r', encoding='utf-8') as f:
            if os.stat(cfinclude_path).st_size == 0:
                return None
            spec = pathspec.PathSpec.from_lines('gitwildmatch', 
                                              [line.rstrip() for line in f])
            return spec
    else:
        return None


def display_and_select_files(folder_path, ui=UserInterface()):
    """Display directory structure as a tree and allow selection"""
    console = Console()
    selections = {}
    git_ignore_spec = get_gitignore_spec(folder_path)
    cf_ignore_spec = get_cfignore_spec(folder_path)
    cf_include_spec = get_cfinclude_spec(folder_path)

    def build_tree(directory, parent_tree, prefix=""):
        try:
            items = sorted(os.listdir(directory))
            for item in items:
                full_path = os.path.join(directory, item)
                rel_path = os.path.relpath(full_path, folder_path)
                
                if ((git_ignore_spec and git_ignore_spec.match_file(rel_path)) or 
                    (cf_ignore_spec and cf_ignore_spec.match_file(rel_path))):
                    continue

                if os.path.isdir(full_path):
                    should_include_dir = True
                    if cf_include_spec:
                        should_include_dir = any(
                            cf_include_spec.match_file(os.path.relpath(os.path.join(root, name), folder_path))
                            for root, dirs, files in os.walk(full_path)
                            for name in files + dirs
                        )
                    
                    if should_include_dir:
                        dir_size = ui.get_directory_size(full_path)
                        branch = parent_tree.add(f"📁 {item} | {ui.convert_size(dir_size)}")
                        path_key = f"{prefix}/{item}"
                        selections[path_key] = True
                        build_tree(full_path, branch, path_key)
                else:
                    if cf_include_spec and not cf_include_spec.match_file(rel_path):
                        continue
                        
                    path_key = f"{prefix}/{item}"
                    selections[path_key] = True
                    file_size = os.path.getsize(full_path)
                    parent_tree.add(f"📄 {item} | {ui.convert_size(file_size)}")
        except PermissionError:
            pass

    # Build initial tree
    root_tree = Tree(f"📁 {folder_path}")
    build_tree(folder_path, root_tree)

    # Display tree
    console.print(root_tree)

    # Allow selection/deselection
    while True:
        questions = [
            inquirer.Path(
                'path',
                message="Enter path to toggle inclusion state. Enter 'done' to finish",
            )
        ]

        answer = inquirer.prompt(questions)
        path = answer['path']

        if path.lower() == 'done':
            break
        
        if len(path) == 0:
            ui.show_message("\nPath cannot be empty. Please enter a valid path or 'done' if you are finished...", Fore.RED)
            continue
        if path[0] != '/':
            path = '/' + path

        if path in selections:
            selections[path] = not selections[path]
            # Toggle all children if it's a directory
            if not path.endswith("/"):
                prefix = path + "/"
            for key in selections:
                if key.startswith(prefix):
                    selections[key] = selections[path]

            # Show current selection state
            print(f"\nToggled {path} to {selections[path]}\n")
        else:
            print(f"\nInvalid path. Please select from the tree above.\n")

    # Return list of selected files
    selected_files = [
        os.path.join(folder_path, path.lstrip("/"))
        for path, selected in selections.items()
        if selected and os.path.isfile(os.path.join(folder_path, path.lstrip("/")))
    ]

    return selected_files

def consolidate_files(folder_path, output_file, ui=UserInterface(), max_file_size_kb=100, max_total_size_mb=5):
    """Consolidate selected files into single output
    
    Args:
        folder_path: Path to the project folder
        output_file: Path to the output file
        ui: UserInterface instance
        max_file_size_kb: Maximum size of individual files to include (in KB)
        max_total_size_mb: Maximum total size of all files combined (in MB)
    """
    selected_files = display_and_select_files(folder_path, ui)
    
    # Filter files based on size limit
    filtered_files = []
    total_size_bytes = 0
    max_total_size_bytes = max_total_size_mb * 1024 * 1024
    max_file_size_bytes = max_file_size_kb * 1024
    
    for file_path in selected_files:
        file_size = os.path.getsize(file_path)
        
        # Skip files larger than max_file_size_kb
        if file_size > max_file_size_bytes:
            ui.show_message(f"Skipping {file_path} (size: {ui.convert_size(file_size)}) - exceeds max file size limit of {max_file_size_kb}KB", Fore.YELLOW)
            continue
            
        # Check if adding this file would exceed the total size limit
        if total_size_bytes + file_size > max_total_size_bytes:
            ui.show_message(f"Stopping at {file_path} - total size would exceed {max_total_size_mb}MB limit", Fore.YELLOW)
            break
            
        filtered_files.append(file_path)
        total_size_bytes += file_size
    
    # If no files were selected after filtering, show a warning
    if not filtered_files:
        ui.show_message("Warning: No files were selected after applying size filters.", Fore.RED)
        return 1

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(f'{os.path.abspath(folder_path)}\n\nThe following content is a collection of files from a project repository. It contains code, documentation, configuration and other text files. The file is delimited to represent each file within the project:\n\nFileStart: <file_path>\n<file_content>\nFileStop: <file_path>\n\n Use all files in this collection to assist the user in producing high quality documentation.\n\n')

        for file_path in filtered_files:
            outfile.write(f"\nFILESTART: {file_path}\n")
            print(f"Reading {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
            except UnicodeDecodeError:
                print(f"Error reading {file_path}. Skipping...")
                print("Consider adding the file to .cfignore if it's a binary file.")
            outfile.write(f"\nFILESTOP: {file_path}\n")
    print(f"\nConsolidated output written to: {os.path.abspath(output_file)}\n")
    file_size_kb = os.path.getsize(output_file) / 1024
    hr_file_size = ui.convert_size(os.path.getsize(output_file))
    if file_size_kb > 750:
        ui.show_message(f"Warning: Output file size is {hr_file_size}. Consider excluding files that are not necessary for project understanding.\n", Fore.RED)
    else:
        ui.show_message(f"Output file size is {hr_file_size}.\n", Fore.MAGENTA)
    return 0
