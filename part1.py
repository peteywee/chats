import os
import json
import PySimpleGUI as sg

def load_large_file(filepath):
    """
    Determines the file type by its extension and loads the file.
    Returns a tuple: (file_type, content)
      - file_type is a string: 'json', 'html', or 'text'
      - content is the parsed JSON object if a JSON file,
        or the full text content if an HTML/text file.
    """
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.json':
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                return 'json', content
            except json.JSONDecodeError as e:
                sg.popup_error("Error decoding JSON:", e)
                return None, None
    elif ext == '.html':
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return 'html', content
    else:
        # For any other extension, treat it as plain text (or HTML if you prefer)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return 'text', content

def create_initial_dictionary():
    """
    Creates an initial dictionary structure for your project.
    It has separate keys to store HTML/text content and JSON content.
    """
    return {
        'project': {
            'title': 'My Project',
            'html_content': '',   # For HTML or plain text content
            'json_content': {}    # For structured JSON data
        }
    }

def main():
    # Set up a dark theme for the GUI (works well on KDE and other desktop environments)
    sg.theme('DarkGrey13')
    
    # Define a simple GUI layout with a file browser and two buttons
    layout = [
        [sg.Text("Upload a large JSON or HTML file:")],
        [sg.Input(key="-FILEPATH-"), sg.FileBrowse()],
        [sg.Button("Load File"), sg.Button("Exit")]
    ]
    
    window = sg.Window("File Upload MVP", layout)
    
    # Create the initial dictionary
    my_dict = create_initial_dictionary()
    
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        elif event == "Load File":
            filepath = values["-FILEPATH-"]
            if not filepath:
                sg.popup_error("No file selected!")
                continue
            
            file_type, content = load_large_file(filepath)
            if file_type is None:
                # There was an error loading the file (e.g., bad JSON), so skip further processing
                continue

            # Update the dictionary based on file type
            if file_type == 'json':
                my_dict['project']['json_content'] = content
                sg.popup("Loaded JSON file successfully!", 
                         "Snippet of JSON content:",
                         json.dumps(content, indent=2)[:500])
            elif file_type in ('html', 'text'):
                my_dict['project']['html_content'] = content
                sg.popup("Loaded HTML/Text file successfully!",
                         "Snippet of file content:",
                         content[:500])
            
            # Optionally, print the updated dictionary in the console for verification
            print("Updated Dictionary:")
            print(json.dumps(my_dict, indent=2))
    
    window.close()

if __name__ == "__main__":
    main()
