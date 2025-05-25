
# Streamdump

Streamdump is a fullstack app that allows you to download video files (including premium or login-based) and upload them directly to your OneDrive Business account using the Microsoft Graph API.

### 🔧 Features:
- ✅ Upload directly to OneDrive Business (25TB+ supported)
- ✅ Supports JSON, TXT, and raw cookie input for downloading protected videos
- ✅ Automatically uses yt-dlp to download
- ✅ Uploads using Microsoft's chunked upload for large files
- ✅ Frontend form for easy use
- ✅ Backend queue processor for handling multiple requests

---

### ⚙ How to Use:
1. Go to the main form.
2. Enter a valid video URL.
3. Provide your OneDrive `Client ID`, `Tenant ID`, and `Client Secret`.
4. Upload your cookies (`.json` or `.txt`), or paste raw cookie text.
5. Hit **Submit**.

---

### 🔐 Security
Each user's credentials are only used for their session. Nothing is stored long-term.

---

### 🧠 Tech Stack:
- Python + Flask (Backend)
- HTML (Frontend)
- yt-dlp (Downloader)
- Microsoft Graph API (Uploader)
