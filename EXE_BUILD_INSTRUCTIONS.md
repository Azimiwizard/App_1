# Building the Stitch Daily Menu App as an Executable

This guide explains how to build the Flask-based Stitch Daily Menu application into a standalone executable (.exe) file for Windows using PyInstaller.

## Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed.
2. **Virtual Environment**: It's recommended to use a virtual environment.
3. **Dependencies**: Install all required packages from `requirements.txt`.

## Installation Steps

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Install Application Dependencies

```bash
pip install -r requirements.txt
```

### 3. Build the Executable

Run the following command to build the executable:

```bash
pyinstaller main.spec
```

This will create a `dist/` directory containing the executable file `stitch_daily_menu.exe`.

## Running the Executable

1. Navigate to the `dist/` directory.
2. Double-click `stitch_daily_menu.exe` to run the application.
3. The app will start a local web server (usually on http://127.0.0.1:5000).
4. Open your web browser and navigate to the displayed URL.

## Important Notes

- **Database**: The app uses SQLite by default. The database file will be created in the same directory as the executable.
- **Uploads**: Image uploads will be stored in a `static/uploads/` subdirectory relative to the executable.
- **Port**: The app runs on port 5000 by default. If this port is busy, you may need to modify the code.
- **Admin Setup**: To create an admin user, run the app once, register a user, then use the Flask CLI command `flask make_admin` (you'll need to set up Flask CLI for this).
- **Firewall**: Windows may prompt you to allow the application through the firewall for network access.

## Troubleshooting

- **Missing DLLs**: If you encounter missing DLL errors, ensure all dependencies are properly installed.
- **Database Issues**: Make sure the application has write permissions in its directory for the database file.
- **Port Conflicts**: If port 5000 is in use, modify the `main.py` file to use a different port.

## File Structure After Build

```
dist/
├── stitch_daily_menu.exe  # Main executable
├── templates/             # Copied templates
├── static/                # Copied static files
└── instance/              # Database directory
```

## Alternative Build Options

### One-File Executable (Larger but Portable)

```bash
pyinstaller --onefile --windowed main.py
```

This creates a single executable file that includes all dependencies.

### Console Version (For Debugging)

```bash
pyinstaller --console main.py
```

This version shows a console window with debug output.

## Low-Budget Deployment Considerations

- **File Size**: The executable will be larger than the source code but eliminates the need for users to install Python and dependencies.
- **Distribution**: You can distribute just the executable and the necessary folders (templates, static, instance).
- **Updates**: To update the app, you'll need to rebuild and redistribute the executable.
- **Database Backup**: Remind users to backup their `instance/stitch_menu.db` file before updates.

## Support

If you encounter issues during the build process, ensure all dependencies are correctly installed and that you're using a compatible Python version.
