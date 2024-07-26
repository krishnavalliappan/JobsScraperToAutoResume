import os

def process_directory(directory, output_file):
    for root, dirs, files in os.walk(directory):
        # Exclude specific directories
        exclude_dirs = ["ResumeTemplates", "OutputResumes", ".vscode", "node_modules", ".venv"]
        for exclude_dir in exclude_dirs:
            if exclude_dir in dirs:
                dirs.remove(exclude_dir)
        
        # Filter for .py files only
        py_files = [file for file in files if file.endswith('.py')]
        
        # Exclude specific .py files
        exclude_files = ["turn_into_onefile.py"]
        for exclude_file in exclude_files:
            if exclude_file in py_files:
                py_files.remove(exclude_file)
        
        for file in py_files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                output_file.write(f"File: {relative_path}\n")
                output_file.write("=" * 50 + "\n")
                output_file.write(content)
                output_file.write("\n\n" + "=" * 50 + "\n\n")
            except Exception as e:
                output_file.write(f"File: {relative_path}\n")
                output_file.write("=" * 50 + "\n")
                output_file.write(f"Error reading file: {str(e)}\n")
                output_file.write("\n\n" + "=" * 50 + "\n\n")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file_path = os.path.join(script_dir, 'output.txt')

    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        process_directory(script_dir, output_file)

    print(f"Output written to {output_file_path}")

if __name__ == "__main__":
    main()
