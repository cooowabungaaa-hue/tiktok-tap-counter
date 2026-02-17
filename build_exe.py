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

    print("\nBuild completed! Check the 'dist' folder for your executables.")

if __name__ == "__main__":
    build()
