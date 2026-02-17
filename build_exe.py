import PyInstaller.__main__
import os
import shutil

def build():
    print("Starting build process...")
    
    # 1. Build Main Application
    print("Building TikTokTapCounter...")
    PyInstaller.__main__.run([
        "app.py",
        "--name=TikTokTapCounter",
        "--onefile",
        # "--noconsole", # Keep console for debugging for now, user requested ease of use but also transparency helps
        "--add-data=templates;templates",
        "--clean",
    ])
    
    # 2. Build Updater
    print("Building Updater...")
    PyInstaller.__main__.run([
        "updater.py",
        "--name=updater",
        "--onefile",
        "--console", # Updater needs console to show progress
        "--clean",
    ])

    # ... (previous build steps) ...

    # 3. Create Zip Package
    print("Creating release package...")
    dist_dir = "dist"
    zip_name = os.path.join(dist_dir, "tiktok-live-tap-counter.zip")
    
    # Files to include
    files_to_zip = [
        os.path.join(dist_dir, "TikTokTapCounter.exe"),
        os.path.join(dist_dir, "updater.exe")
    ]
    
    import zipfile
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_zip:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))
                print(f"Added {file} to zip.")
            else:
                print(f"Warning: {file} not found!")

    print(f"\nBuild & Packaging completed! Release zip is ready at: {zip_name}")

if __name__ == "__main__":
    build()
