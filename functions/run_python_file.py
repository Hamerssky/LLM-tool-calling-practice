import os
import subprocess

from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a specified python file (file_path) relative to the working directory, with arguments if provided",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the python file which you want to execute, relative to the working directory, if file doesn't end with .py, it will throw an error",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Additional arguments for the python file, provided as an array of strings (default is None)",
                items = types.Schema(
                    type=types.Type.STRING,
                )
            ),
        },
        required=["file_path"],
    ),
)

def run_python_file(working_directory, file_path, args=None):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if file_path.split(".")[-1] != "py":
            return f'Error: "{file_path}" is not a Python file'
        command = ["python", target_file]
        if args:
            for arg in args:
                command.extend(str(arg))
        process = subprocess.run(command, text=True, capture_output=True, timeout=30)
        output = ""
        if process.returncode:
            output += f"Process exited with code {process.returncode}\n"
        if not process.stdout:
            output += f"STDOUT: No output produced\n"
        else:
            output += f"STDOUT: {process.stdout}\n"
        if not process.stderr:
            output += f"STDERR: No output produced\n"
        else:
            output += f"STDERR: {process.stderr}\n"
        return output
    except Exception as e:
        return f"Error: executing Python file: {e}"