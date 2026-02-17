# How to Publish Your TikTok Live Tap Counter

Congratulations! Your application is ready for distribution. Follow these steps to publish it on GitHub so Yokoyan can download it.

## 1. Push Code to GitHub

First, upload your code to the repository you created.

1.  Open your terminal/command prompt.
2.  Navigate to the project folder (if not already there):
    ```powershell
    cd C:\Users\小野明子\.gemini\antigravity\scratch\tiktok-live-tap-counter
    ```
3.  Add all files and commit:
    ```powershell
    git add .
    git commit -m "Initial release with updater and setup guide"
    ```
4.  Push to GitHub (you may be asked to sign in):
    ```powershell
    git branch -M main
    git push -u origin main
    ```

## 2. Create a Release

1.  Go to your repository: [https://github.com/cooowabungaaa-hue/tiktok-tap-counter](https://github.com/cooowabungaaa-hue/tiktok-tap-counter)
2.  Click on **Releases** on the right sidebar (or "Create a new release").
3.  Click **Draft a new release**.
4.  **Tag version**: `v1.0.0` (Must match `version.json`).
5.  **Release title**: `v1.0.0 - Initial Release`.
6.  **Description**: "First release with auto-update support."
7.  **Attach binaries**:
    -   Go to the `dist` folder on your computer.
    -   Select both `TikTokTapCounter.exe` and `updater.exe`.
    -   **Important**: Create a ZIP file named `tiktok-live-tap-counter.zip` containing both `.exe` files.
    -   Upload `tiktok-live-tap-counter.zip` to the release.
8.  Click **Publish release**.

## 3. Enable GitHub Pages (for Updates & Landing Page)

The app checks `version.json` from your GitHub Pages site.

1.  Go to **Settings** > **Pages** in your repository.
2.  Under **Source**, select `Deploy from a branch`.
3.  Select `main` branch and `/ (root)` folder (or `/docs` if you moved `dist-site` there, but root is fine for now if `index.html` is in root. **WAIT**: We put the landing page in `dist-site`.
    -   **Action**: You should probably move the contents of `dist-site` to the root OR configure Pages to look at `dist-site`. GitHub Pages usually only supports `/` or `/docs`.
    -   *Recommendation*: Move `dist-site/index.html` to `index.html` in the root for simplicity, OR use a GitHub Action.
    -   *Easiest*: Let's stick to the current structure. You can set the "Source" to `main` branch. Then your site will be at `.../dist-site/`.
    -   **Correction**: The `UPDATE_URL` in `app.py` needs to match where `version.json` ends up.
    -   If `version.json` is in the root of the repo, the URL is `https://cooowabungaaa-hue.github.io/tiktok-tap-counter/version.json`.  
    -   Ensure `version.json` is pushed to the root (it is!).

## 4. Share the Link

Send this link to Yokoyan:  
`https://cooowabungaaa-hue.github.io/tiktok-tap-counter/dist-site/`  
(or wherever the `index.html` ends up).

## Checklist for Next Time

-   Update `version.json` (e.g., to `1.0.1`).
-   Update `VERSION` in `app.py`.
-   Run `python build_exe.py`.
-   Commit and push.
-   Create new GitHub Release `v1.0.1` with new zip.
