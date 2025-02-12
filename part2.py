#!/usr/bin/env python3
import json
import PySimpleGUI as sg
import os
import re

def create_initial_dictionary():
    """
    Creates the base dictionary structure.
    """
    return {
        "project": {
            "title": "My Project",
            "description": "",   # Text/HTML content
            "json_content": {},  # JSON file content
            "conversations": {}  # Extracted conversation segments
        }
    }

def load_file(filepath):
    """ Reads file content as text """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def load_json_file(filepath):
    """ Loads JSON content """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_conversations(text):
    """
    Extracts basic conversation-like segments from text.
    Example: Lines starting with 'Speaker: Message'
    """
    pattern = r'(\w+): (.+)'
    matches = re.findall(pattern, text)
    conversations = {f"line_{i}": {"speaker": m[0], "message": m[1]} for i, m in enumerate(matches)}
    return conversations

def detect_file_type(filepath):
    """ Detects file type based on extension """
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ['.json']:
        return "json"
    elif ext in ['.txt', '.html', '.htm']:
        return "text"
    return "unknown"

def main():
    sg.theme('DarkGrey13')

    data_dict = create_initial_dictionary()
    last_saved_state = json.dumps(data_dict, indent=2)

    layout = [
        [sg.TabGroup([
            [sg.Tab('Upload File', [
                [sg.Text("Drop or select a file:"), sg.Input(key="-FILEPATH-", enable_events=True), sg.FileBrowse()],
                [sg.Button("Auto Load File"), sg.Button("Extract Conversations")],
                [sg.Multiline("", size=(80, 6), key="-STATUS-", disabled=True)]
            ]),
            sg.Tab('Edit Dictionary', [
                [sg.Text("Edit Dictionary (JSON Format):")],
                [sg.Multiline(json.dumps(data_dict, indent=2), size=(80, 20), key="-DICT_EDIT-")],
                [sg.Button("Update Dictionary"), sg.Button("Format JSON"), sg.Button("Revert Changes")],
                [sg.Button("Save Dictionary"), sg.Button("Refresh View")]
            ]),
            sg.Tab('Live Preview', [
                [sg.Text("HTML Preview (if applicable):")],
                [sg.Multiline("", size=(80, 20), key="-HTML_PREVIEW-", disabled=True)]
            ])]
        ])]
    ]

    window = sg.Window("Enhanced Dictionary Editor", layout, finalize=True, resizable=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        # ----- File Upload Tab -----
        if event == "Auto Load File":
            filepath = values["-FILEPATH-"]
            if not filepath:
                sg.popup_error("No file selected!")
                continue

            file_type = detect_file_type(filepath)
            try:
                if file_type == "json":
                    json_data = load_json_file(filepath)
                    data_dict["project"]["json_content"] = json_data
                    data_dict["project"]["description"] = ""
                    window["-STATUS-"].update(f"Loaded JSON file:\n{filepath}")
                elif file_type == "text":
                    text_content = load_file(filepath)
                    data_dict["project"]["description"] = text_content
                    data_dict["project"]["json_content"] = {}
                    window["-STATUS-"].update(f"Loaded text file:\n{filepath}")
                    window["-HTML_PREVIEW-"].update(text_content if "<html" in text_content.lower() else "Not an HTML file.")
                else:
                    sg.popup_error("Unsupported file type!")
                    continue

                last_saved_state = json.dumps(data_dict, indent=2)
                window["-DICT_EDIT-"].update(last_saved_state)

            except Exception as e:
                sg.popup_error(f"Error loading file:\n{e}")

        if event == "Extract Conversations":
            text_content = data_dict["project"].get("description", "")
            if not text_content:
                sg.popup_error("No text content available for extraction.")
            else:
                conversations = extract_conversations(text_content)
                data_dict["project"]["conversations"] = conversations
                sg.popup("Conversations extracted!")
                window["-DICT_EDIT-"].update(json.dumps(data_dict, indent=2))

        # ----- Edit Dictionary Tab -----
        if event == "Update Dictionary":
            try:
                updated_text = values["-DICT_EDIT-"]
                data_dict = json.loads(updated_text)
                sg.popup("Dictionary updated successfully!")
            except Exception as e:
                sg.popup_error(f"Invalid JSON format:\n{e}")

        if event == "Format JSON":
            try:
                formatted_json = json.dumps(json.loads(values["-DICT_EDIT-"]), indent=2)
                window["-DICT_EDIT-"].update(formatted_json)
            except Exception as e:
                sg.popup_error(f"Error formatting JSON:\n{e}")

        if event == "Revert Changes":
            window["-DICT_EDIT-"].update(last_saved_state)
            sg.popup("Reverted to last saved state.")

        if event == "Save Dictionary":
            filename = sg.popup_get_file("Save dictionary to file", save_as=True, file_types=(("JSON Files", "*.json"),))
            if filename:
                try:
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(data_dict, f, indent=2)
                    sg.popup("Dictionary saved successfully!")
                    last_saved_state = json.dumps(data_dict, indent=2)
                except Exception as e:
                    sg.popup_error(f"Error saving dictionary:\n{e}")

        if event == "Refresh View":
            window["-DICT_EDIT-"].update(json.dumps(data_dict, indent=2))

    window.close()

if __name__ == "__main__":
    main()
