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
 
## 🆕 Schedule (Live TV & Catchup)
The **Schedule** section displays NHK World’s daily programming guide, including both upcoming and past programs.
- **Features:**
  - Lists programs by **time range** (e.g. `10:00–10:30 NHK NEWSLINE`)
  - Converts times from **Japan Standard Time (JST)** to **your local timezone**
  - Supports both **local view** and **Tokyo time view** (switch in *Settings → View schedule by Tokyo time (JST)*)
  - **Color-coded programs:**
    - 🟩 *Green*: Past programs (available for playback)
    - 🟦 *Cyan*: Live Now (currently airing)
    - ⚪ *Light Grey*: Upcoming programs (not yet available)
  - "Today" is dynamically highlighted based on both Tokyo and local time zones  
    (e.g., if Tokyo and your location are on different days, both “Local Today” and “Tokyo Today” are indicated)

**Playback Behavior:**
- Clicking on a past program immediately starts playback (catch-up stream)
- Clicking on a live program plays the live stream
- Clicking on a future program shows a notice:  
  *“This program is not yet available.”*
- Use the context menu to open the relevant show.
---
### 🆕 Search (News & Shows)
Unified and improved **search interface** modeled after YouTube’s search experience.
  - Supports both **program titles** and **episode titles**
  - Fully playable VOD results and show detail pages
  - Displays thumbnails, show names, and descriptions

---

### ⚙️ Settings Options
- **Content Language:** Choose your preferred interface language
- **Use Color in Main Menu:** Enable/disable color styling in the main menu
- **View schedule by Tokyo time (JST):** Toggle between Tokyo or local timezone display for the schedule
- **Font Tip:** When using Japanese, Chinese, or Korean, set your Kodi font to Arial for best display.
---

### 🧩 Notes
- All times are automatically converted using Kodi’s internal timezone setting (`America/New_York`, etc.)
- Addon caches no schedule data — always retrieves the latest JSON from NHK servers
---

## ⚙️ Installation

1. Download or clone this repository:
   ```bash
   git clone https://github.com/usphil/plugin.video.nhkworld.git
2. Copy the folder plugin.video.nhkworld into your Kodi addons directory:
    Kodi/addons/
3. Restart Kodi → Go to: Add-ons → Video Add-ons → NHK World

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

v1.1.0  
Added Search both Shows and News
Added Live & Catch Up 
Code cleanup and optimized load speed

📜 License
This project uses publicly accessible NHK World web data.
It is not affiliated with or endorsed by NHK.
For personal and educational use only.

👨‍💻 Author

Developed and maintained by usphil
