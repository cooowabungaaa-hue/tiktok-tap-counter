import os
import sys
import time
import requests
import zipfile
import shutil
import subprocess

def download_and_update(download_url, target_exe_path):
    print(f"Starting update from {download_url}...")
    
    # Define paths
    temp_zip = "update.zip"
    extract_folder = "update_extracted"
    
    try:
        # Step 1: Download the new version
        print("Downloading update...")
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        with open(temp_zip, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")

        # Step 2: Wait for main app to close
        print("Waiting for main application to close...")
        time.sleep(2)  # Give it a moment

        # Step 3: Extract the update
        print("Extracting update...")
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder)
        
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
            
        print("Extraction complete.")

        # Step 4: Replace the old executable
        # Assuming the zip contains the new executable with the same name or similar structure
        # We need to find the .exe in the extracted folder
        new_exe_path = None
        for root, dirs, files in os.walk(extract_folder):
            for file in files:
                if file.endswith(".exe") and "updater" not in file:
                     new_exe_path = os.path.join(root, file)
                     break
        
        if not new_exe_path:
            raise Exception("No executable found in the update package.")

        print(f"Replacing {target_exe_path} with {new_exe_path}...")
        
        # Rename user's current exe to .old just in case (Windows won't let us overwrite running exe easily if it's still locked, but we waited)
        # Actually, best practice on Windows: move current exe to .old, move new exe to current location.
        # If .old exists, delete it first.
        old_backup = target_exe_path + ".old"
        if os.path.exists(old_backup):
            os.remove(old_backup)
            
        # Move current running exe (if it's not THIS script) to backup
        # But wait, target_exe_path is the main app. this script is running separately.
        if os.path.exists(target_exe_path):
             os.rename(target_exe_path, old_backup)
        
        shutil.move(new_exe_path, target_exe_path)
        print("Update applied successfully.")

        # Step 5: Cleanup
        print("Cleaning up temporary files...")
        if os.path.exists(temp_zip):
            os.remove(temp_zip)
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)

        # Step 6: Restart the application
        print("Restarting application...")
        subprocess.Popen([target_exe_path])
        print("Done! Exiting updater.")
        sys.exit(0)

    except Exception as e:
        print(f"Update failed: {e}")
        input("Press Enter to close...")
        sys.exit(1)

if __name__ == "__main__":
    # Usage: updater.exe <download_url> <target_exe_path>
    if len(sys.argv) < 3:
        print("Usage: updater.exe <download_url> <target_exe_path>")
        # For testing purposes or manual run
        input("Press Enter to close...")
        sys.exit(1)
    
    url = sys.argv[1]
    target = sys.argv[2]
    
    # Wait a bit more to ensure the calling process is fully dead
    time.sleep(3)
    
    download_and_update(url, target)
