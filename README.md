# NHK World Kodi Addon

Watch **NHK World Live TV**, news, and on-demand programs directly in **Kodi**.  
This addon retrieves official NHK World content from public NHK APIs, with multilingual support.

---

## ✨ Features

- 🎥 **NHK World Live TV** — Full HD (1080p) stream with automatic fallback to 720p  
- 🗂️ **Programs** — Browse NHK World programs by category or show  
- 📰 **News** — Latest NHK World news videos (Japan, Asia, World, etc.)  
- 🔍 **Search** — Find NHK videos and news by keyword  
- 🌐 **Multilingual Interface** — Choose from 15+ supported languages  
- 🧩 **CoreELEC / LibreELEC Compatible** — Optimized for embedded Kodi systems  

---

## ⚙️ Installation

1. Download or clone this repository:
   ```bash
   git clone https://github.com/usphil/plugin.video.nhkworld.git
2. Copy the folder plugin.video.nhkworld into your Kodi addons directory:
    Kodi/addons/
3. Restart Kodi → Go to: Add-ons → Video Add-ons → NHK World

🧠 Technical Notes
Live stream URLs are dynamically parsed from
https://www3.nhk.or.jp/nhkworld/common/assets/live/js/main.js
ensuring up-to-date sources.
Stream preference order: 
1080p (.../o-master.m3u8)
Parsed fallback (720p)
Static backup URL
Supports application/x-mpegURL for inputstream.adaptive

⚙️ Settings
Content Language: Choose your preferred NHK World language
Font Tip: When using Japanese, Chinese, or Korean, set your Kodi font to Arial for best display.

🧩 Compatibility
Kodi 20.x “Nexus”
Kodi 21.x “Omega”
Tested on:
CoreELEC 21.2
LibreELEC
Windows 10/11
Ubuntu 22.04

## 🌐 DNS Optimization (Recommended)
If you ever encounter the error: 
NameResolutionError: Failed to resolve 'media-tyo.hls.nhkworld.jp'
or program lists load slowly 
this is most likely due to your Internet provider’s default DNS server being slow or restrictive.

✅ **Recommended fix:**  
Change your device to use a faster, public DNS service.

| Provider | Primary DNS | Secondary DNS |
|-----------|--------------|---------------|
| **Cloudflare** | 1.1.1.1 | 1.0.0.1 |
| **Google DNS** | 8.8.8.8 | 8.8.4.4 |
| **Quad9 (Secure)** | 9.9.9.9 | 149.112.112.112 |

💡 Even if the addon works normally, switching to a faster DNS (like Cloudflare or Google) is **highly recommended** — it improves connection stability, API response speed, and live-stream playback performance.

🧾 Changelog
v1.0.0 — Initial Release
Added Live TV (1080p with fallback)
Added Programs and Categories
Added News by region and Top News
Added Multilingual UI and font switching logic
Added Smart Search (auto-play videos)
Code cleanup and optimized load speed

📜 License
This project uses publicly accessible NHK World web data.
It is not affiliated with or endorsed by NHK.
For personal and educational use only.

👨‍💻 Author

Developed and maintained by usphil
