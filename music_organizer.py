from pathlib import Path
from collections import defaultdict
import PyQt6 as qt

# Function to find common substrings among filenames
def find_common_substrings(filenames):
    substring_count = defaultdict(int)

    # Extract base names without extensions and find common substrings
    for filename in filenames:
        base_name = Path(filename).stem.lower()
        for i in range(len(base_name)):
            for j in range(i + 3, len(base_name) + 1):
                if base_name[i-1] != ' ':
                    continue
                if j < len(base_name) and base_name[j] != ' ':
                    continue
                substring = base_name[i:j]
                substring_count[substring] += 1

    # Filter substrings with at least 3 occurrences
    items = list(substring_count.items())
    items.sort(key=lambda x: x[1], reverse=True)

    common_substrings = [substring for substring, count in items if count >= 3]
    common_substrings = [substring for substring in common_substrings if substring.strip() == substring]
    common_substrings = [substring for substring in common_substrings if '-' not in substring]

    print(common_substrings)

    return common_substrings

# Function to organize files into folders based on a common substring
def organize_files(path, common_substring):
    folder_path = path / common_substring
    folder_path.mkdir(exist_ok=True)
    
    for file in path.glob('*'):
        if file.is_file():
            base_name = Path(file).stem
            if common_substring in base_name.lower():
                new_file_path = folder_path / file.name
                file.rename(new_file_path)

# Main function
def main():
    folder_path = Path(input("Enter the path to the folder: "))

    if not folder_path.exists() or not folder_path.is_dir():
        print("Invalid folder path.")
        return

    filenames = [file.name for file in folder_path.glob('*') if file.is_file()]

    if not filenames:
        print("No files found in the folder.")
        return

    common_substrings = find_common_substrings(filenames)

    if not common_substrings:
        print("No common substrings found with at least 3 characters.")
        return

    index = 0
    while index < len(common_substrings):
        common_substring = common_substrings[index]
        print(f"Common substring found: '{common_substring}'")

        confirm = input("Do you want to organize files into folders based on this substring? (yes/no/exit): ")

        if confirm.lower() == 'yes':
            organize_files(folder_path, common_substring)
            print("Files organized into folders successfully.")
        elif confirm.lower() == 'exit':
            break
        else:
            index += 1


if __name__ == "__main__":
    main()
