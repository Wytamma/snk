def open_text_editor(file_path):
    """
    Opens the system's default text editor to edit the specified file.

    Parameters:
    file_path (str): The path to the file to be edited.
    """
    import os
    import platform
    import subprocess

    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(("open", file_path))
    else:  # Linux and other Unix-like systems
        editors = ["nano", "vim", "vi"]
        editor = None
        for e in editors:
            if (
                subprocess.call(
                    ["which", e], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                == 0
            ):
                editor = e
                break
        if editor:
            subprocess.call([editor, file_path])
        else:
            raise Exception(
                "No suitable text editor found. Please install nano or vim."
            )