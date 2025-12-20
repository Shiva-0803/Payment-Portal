import os

file_paths = [
    r'd:/0803/users/templates/users/exam_dashboard.html',
    r'd:/0803/users/templates/users/admin_dashboard.html'
]

for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Explicit replacements for the known error patterns
        new_content = content.replace('selected_branch==code', 'selected_branch == code')
        new_content = new_content.replace('selected_year==year_val', 'selected_year == year_val')
        
        # Generic safety replacement just in case
        new_content = new_content.replace('==', ' == ').replace('  ==  ', ' == ')
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed {file_path}")
        else:
            print(f"No changes needed for {file_path}")
    else:
        print(f"File not found: {file_path}")
