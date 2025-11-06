# -*- coding: utf-8 -*-
from resources.lib import helper
from resources.lib.dict import *
import requests, time, json, re, urllib.parse
import os, sys, xbmc, xbmcvfs, xbmcplugin, xbmcaddon, xbmcgui
from datetime import datetime, timedelta, timezone

NHK_BASE = "https://www3.nhk.or.jp"
API_BASE = "https://api.nhkworld.jp/showsapi/v1/en"
API_BASE_LANG = f"https://api.nhkworld.jp/showsapi/v1/{lang_code}"
HISTORY_FILE = xbmcvfs.translatePath("special://profile/addon_data/plugin.video.nhkworld/search_history.json")
MAX_HISTORY = 10
use_color = addon.getSetting('usecolor')
days_past = int(addon.getSetting("days_past"))
days_future = int(addon.getSetting("days_future"))+1 #1 replacement for today not listed
view_by_tokyo = addon.getSetting("view_by_tokyo") == "true"

def color(name,c=''):
    if use_color == "true" :
        return '[COLOR %s]%s[/COLOR]'%(c,name) if c else re.sub('\[[^\[]+?\]','',name)
    else:
        c = ""
        return '[COLOR %s]%s[/COLOR]'%(c,name) if c else re.sub('\[[^\[]+?\]','',name)
        
def logs(msg, level=xbmc.LOGDEBUG):
    s = f'*** NHK WORLD ***  {msg}'
    xbmc.log(s, xbmc.LOGINFO)
    
def xsearch(pattern,string,group=1,flags=0,result=''):
    try:response=re.search(pattern,string,flags).group(group)
    except:response=result
    return response
        
class myAddon(helper.myAddon):
    def __init__(self):
        helper.myAddon.__init__(self)
        self.thumb = self.addonIcon
        self.fanart = self.addonFanart

    def SearchHub(self, url, ilist):
        """
        Phase 1: Search Hub.
        """
        ilist = self.addMenuItem(
            color("New Search", "green"),
            "SEARCH_ALL_KEYBOARD",
            ilist,
            "",
            self.thumb,
            self.fanart,
            {"Title": "New search", "Plot": "Enter a new keyword"},
            isFolder=False
        )

        history = []
        if xbmcvfs.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception as e:
                logs(f"Error reading search history: {e}")
                history = []

        if history:
            ilist = self.addMenuItem(
                color("Clear Search History", "red"),
                "CLEAR_HISTORY",
                ilist,
                "",
                self.thumb,
                self.fanart,
                {"Title": "Clear History", "Plot": "Delete all previous search keywords"},
                isFolder=False
            )

            for kw in history:
                li = xbmcgui.ListItem(f"{kw}")
                li.setArt({"icon": self.thumb, "fanart": self.fanart})
                li.setInfo("video", {"title": kw, "plot": "Search previous keyword"})
                li.setProperty("IsFolder", "true")

                delete_url = f"{sys.argv[0]}?mode=DELETE_KEYWORD&url={urllib.parse.quote_plus(kw)}"
                li.addContextMenuItems([
                    ("Delete this keyword", f'RunPlugin({delete_url})')
                ])

                url = f"{sys.argv[0]}?mode=SEARCH_ALL_MENU&url={urllib.parse.quote_plus(kw)}"
                ilist.append((url, li, True))

        return self.endDirectory(ilist)

    def SearchKeyboard(self, url, ilist):
        """
        Phase 2: Open keyboard input new keyword
        """
        kb = xbmc.Keyboard('', 'Enter search keyword')
        kb.doModal()
        if not kb.isConfirmed():
            return ilist

        keyword = kb.getText().strip()
        if not keyword:
            return ilist

        self.addKeywordToHistory(keyword)
        q = urllib.parse.quote_plus(keyword)
        target_url = f"{sys.argv[0]}?mode=SEARCH_ALL_MENU&url={q}"
        xbmc.executebuiltin(f'Container.Update({target_url}, replace)')
        return []
        
        ilist = self.addMenuItem(
            f"Search NEWS for: {keyword}",
            "SEARCH_NEWS_RESULT",
            ilist,
            f"https://api.nhkworld.jp/nwapi/search/nhkworld@en@news/0/50/{urllib.parse.quote_plus(keyword)}/list.json",
            self.thumb,
            self.fanart,
            {"Title": keyword, "Plot": "Search results from NHK News"},
            isFolder=True
        )

        ilist = self.addMenuItem(
            f"Search SHOWS for: {keyword}",
            "SEARCH_SHOWS_RESULT",
            ilist,
            keyword,
            self.thumb,
            self.fanart,
            {"Title": keyword, "Plot": "Search results from NHK Shows"},
            isFolder=True
        )
        return ilist
        return self.endDirectory(ilist)

    def SearchAllMenu(self, keyword, ilist):
        """
        Phase 2b: when chose old keyword — shows 2 options NEWS / SHOWS
        """
        ilist = self.addMenuItem(
            f"Search NEWS for: {keyword}",
            "SEARCH_NEWS_RESULT",
            ilist,
            f"https://api.nhkworld.jp/nwapi/search/nhkworld@en@news/0/50/{urllib.parse.quote_plus(keyword)}/list.json",
            self.thumb,
            self.fanart,
            {"Title": keyword, "Plot": "Search results from NHK News"},
            isFolder=True
        )
        ilist = self.addMenuItem(
            f"Search SHOWS for: {keyword}",
            "SEARCH_SHOWS_RESULT",
            ilist,
            keyword,
            self.thumb,
            self.fanart,
            {"Title": keyword, "Plot": "Search results from NHK Shows"},
            isFolder=True
        )
        return self.endDirectory(ilist)

    def SearchNewsResult(self, url, ilist):
        """
        Phase 2: Load results from NHK API and show playable videos only
        """
        try:
            r = requests.get(url, headers=self.defaultHeaders, timeout=10)
            data = r.json()
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Search", f"Error: {e}", xbmcgui.NOTIFICATION_ERROR)
            return ilist

        results = data.get("hits", {}).get("hits", [])
        if not results:
            xbmcgui.Dialog().notification("NHK Search", "No results found", xbmcgui.NOTIFICATION_INFO)
            return ilist

        for item in results:
            src = item.get("_source", {})
            if not src:
                continue

            title = src.get("title", "No title")
            desc = src.get("description", "")
            link = src.get("url", "")
            thumb = src.get("thumbnail", "")
            duration = src.get("duration", "")
            if not duration:
                continue
            if link.startswith("/"):
                link = "https://www3.nhk.or.jp" + link
            if thumb.startswith("/"):
                thumb = "https://www3.nhk.or.jp" + thumb

            info = {
                "title": title,
                "plot": desc,
                "duration": duration,
                "studio": "NHK World",
                "mediatype": "video"
            }
            ilist = self.addEpisode(title, "PLAY_NEWS", ilist, link, thumb, thumb, info)

        return ilist

    def SearchShowsResult(self, keyword, ilist):
        base_url = "https://api.nhkworld.jp/showsapi/v1/en/video_episodes"
        found = set()
        kw = keyword.lower()
        kw = urllib.parse.quote_plus(keyword)

        for offset in range(0, 3000, 100):  
            url = f"{base_url}?limit=100&offset={offset}"
            try:
                data = requests.get(url, headers=self.defaultHeaders, timeout=10).json()
            except Exception as e:
                xbmcgui.Dialog().notification("NHK Error", str(e), xbmcgui.NOTIFICATION_ERROR)
                return ilist

            items = data.get("items", [])
            if not items:
                break
            for item in items:
                try:
                    title = str(item.get("title", ""))
                    prog = item.get("video_program", {})
                    prog_title = str(prog.get("title", ""))
                    pid = prog.get("id", "" )
                    prog_url = f"{API_BASE}/video_programs/{pid}/video_episodes"
                    vid = item.get("video", {})
                    ep_url = vid.get("url")

                    # match episode title
                    if kw in title.lower() and ep_url not in found:
                        thumb = NHK_BASE + item["images"][1]["url"] if item.get("images") else self.thumb
                        desc = item.get("description", "")

                        found.add(ep_url)
                        ilist = self.addEpisode(title, "PLAY_EPISODE", ilist, ep_url, thumb, thumb, {"plot": desc})

                    # match program title
                    elif kw in prog_title.lower() and prog_url not in found:
                        found.add(prog_url)
                        thumb = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQfW1HW_chFm6ge8Mh9ZC8koNUAfz45DqMFNA&s"
                        ilist = self.addMenuItem(color(prog_title, "red"), "EPISODES_LIST", ilist, prog_url, thumb, thumb, {}, isFolder=True)
                    
                except Exception as e:
                    logs(f"Fallback parse failed: {e}")

        if not found:
            xbmcgui.Dialog().notification("NHK Live", "No results found.", xbmcgui.NOTIFICATION_INFO, 3000)
            
        return ilist

    def addKeywordToHistory(self, keyword):
        try:
            history = []
            if xbmcvfs.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            if keyword in history:
                history.remove(keyword)
            history.insert(0, keyword)
            history = history[:MAX_HISTORY]
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logs(f"Error saving search history: {e}")
            
    def ClearHistory(self, url, ilist):
        if xbmcvfs.exists(HISTORY_FILE):
            try:
                xbmcvfs.delete(HISTORY_FILE)
                xbmcgui.Dialog().notification(
                    "NHK Live",
                    "Search history cleared.",
                    xbmcgui.NOTIFICATION_INFO,
                    3000
                )
            except Exception as e:
                xbmcgui.Dialog().notification(
                    "NHK Live",
                    f"Failed to clear history: {e}",
                    xbmcgui.NOTIFICATION_ERROR,
                    3000
                )
        else:
            xbmcgui.Dialog().notification(
                "NHK Live",
                "No search history found.",
                xbmcgui.NOTIFICATION_INFO,
                2000
            )

        xbmc.executebuiltin(f"Container.Update({sys.argv[0]}?mode=SEARCH_HUB, replace)")

    def DeleteKeyword(self, keyword, ilist):
        try:
            if not xbmcvfs.exists(HISTORY_FILE):
                xbmcgui.Dialog().notification("NHK Live", "No search history found.", xbmcgui.NOTIFICATION_INFO, 2000)
                return

            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)

            if keyword in history:
                history.remove(keyword)
                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                xbmcgui.Dialog().notification("NHK Live", f"Deleted '{keyword}'", xbmcgui.NOTIFICATION_INFO, 2000)
            else:
                xbmcgui.Dialog().notification("NHK Live", "Keyword not found.", xbmcgui.NOTIFICATION_INFO, 2000)

            xbmc.executebuiltin(f"Container.Update({sys.argv[0]}?mode=SEARCH_HUB, replace)")

        except Exception as e:
            xbmcgui.Dialog().notification("NHK Live", f"Delete failed: {e}", xbmcgui.NOTIFICATION_ERROR, 3000)

    def get_live_stream(self):
        """Prefer 1080p live stream (media-tyo), fallback to parsed link"""
        headers = {
            "User-Agent": self.defaultHeaders["User-Agent"],
            "Referer": "https://www3.nhk.or.jp/nhkworld/en/live_tv/",
        }
        primary_url = "https://media-tyo.hls.nhkworld.jp/hls/w/live/o-master.m3u8"
        try:
            test = requests.head(primary_url, headers=headers, timeout=5)
            if test.status_code == 200:
                return primary_url
        except Exception as e:
            logs(f"1080p link failed: {e}")

        try:
            js_url = "https://www3.nhk.or.jp/nhkworld/common/assets/live/js/main.js"
            js_text = requests.get(js_url, headers=headers, timeout=10).text
            base_url = xsearch(r'const s=`(.*?)/(master.m3u8|o-master.m3u8)`', js_text)
            if base_url:
                fallback_url = "https://" + base_url.replace("${t}", "w") + "/o-master.m3u8"
                logs(f"Fallback to parsed live stream: {fallback_url}")
                return fallback_url
        except Exception as e:
            logs(f"Fallback parse failed: {e}")

        final_url = "https://masterpl.hls.nhkworld.jp/hls/w/live/master.m3u8"
        logs(f"Fallback to static URL: {final_url}")
        return final_url

    # ========== MAIN MENU ==========

    def MainMenu(self, url, ilist):

        info = {"Title": "Search", "Plot": "Search NHK World News & Shows"}
        ilist = self.addDir(color("Search", "red"), "SEARCH_HUB", ilist, "search_news", self.thumb, self.fanart, info)
        
        live_url = self.get_live_stream()
        info = {"Title": "NHK World Live", "Plot": "Watch NHK World live stream"}
        ilist = self.addVideo(color("Live Now", "green"), "PLAY_EPISODE", ilist, live_url, self.thumb, self.fanart, info)

        info = {"Title": "News", "Plot": "Browse programs through the daily schedule"}
        ilist = self.addDir(color("Live & Catchup", "green"), "SCHEDULE_ITEMS", ilist, "Today Schedule", self.thumb, self.thumb, info)

        info = {"Title": "News", "Plot": "NHK World latest news videos"}
        ilist = self.addDir(color("NHK News", "orange"), "NEWS_MENU", ilist, "news_in_english", self.thumb, self.fanart, info)

        programs_url = f"{API_BASE}/video_programs?limit=100&sort=-date"
        info = {"Title": "Video Programs", "Plot": "Browse NHK World on-demand programs"}
        ilist = self.addDir(color("Latest Shows","orange"), "SHOWS_LIST", ilist, programs_url, self.thumb, self.fanart, info)

        programs_url = f"{API_BASE}/video_programs?limit=20&sort=trending"
        info = {"Title": "Video Programs", "Plot": "Browse NHK World trending programs"}
        ilist = self.addDir(color("Trending","orange"), "SHOWS_LIST", ilist, programs_url, self.thumb, self.fanart, info)

        videos_url = f"{API_BASE}/video_episodes?limit=100&offset=0"
        info = {"Title": "Latest Videos", "Plot": "Browse NHK World on-demand latest videos"}
        ilist = self.addDir(color("Latest Videos", "orange"), "EPISODES_LIST", ilist, videos_url, self.thumb, self.fanart, info)

        cat_url = f"{API_BASE}/categories/"
        info = {"Title": "Categories", "Plot": "Explore NHK World videos by category"}
        ilist = self.addDir(color("Categories", "orange"), "CATEGORIES", ilist, cat_url, self.thumb, self.fanart, info)
        
        info = {"Title": "Other Languages", "Plot": "Explore NHK World programs in other languages"}
        ilist = self.addDir("Other Languages", "SECOND_LANG", ilist, "url", self.thumb, self.fanart, info)
        
        info = {"Title": "Settings", "Plot": "Open the NHK World add-on settings"}
        ilist = self.addDir(color("Settings", "lime"), "OPEN_SETTINGS", ilist, "settings", self.thumb, self.fanart, info)

        return ilist
    
    def openSettings(self, url):
        xbmcaddon.Addon().openSettings()
    
    def SecondLang(self, url, ilist):
        
        info = {"Title": "News", "Plot": "NHK World latest news videos"}
        ilist = self.addDir(color(NHK_NEWS, "cyan"), "NEWS_MENU", ilist, "news2", self.thumb, self.fanart, info)

        programs_url = f"{API_BASE_LANG}/video_programs?limit=100&sort=-date"
        info = {"Title": LATEST_SHOWS, "Plot": SHOW_PLOT}
        ilist = self.addDir(color(LATEST_SHOWS,"cyan"), "SHOWS_LIST", ilist, programs_url, self.thumb, self.fanart, info)

        videos_url = f"{API_BASE_LANG}/video_episodes?limit=100&offset=0"
        info = {"Title": LATEST_VIDEOS, "Plot": VIDEO_PLOT}
        ilist = self.addDir(color(LATEST_VIDEOS, "cyan"), "EPISODES_LIST", ilist, videos_url, self.thumb, self.fanart, info)

        cat_url = f"{API_BASE_LANG}/categories/"
        info = {"Title": CATEGORIES, "Plot": CATEGORY_PLOT}
        ilist = self.addDir(color(CATEGORIES, "cyan"), "CATEGORIES", ilist, cat_url, self.thumb, self.fanart, info)

        info = {"Title": "Change Language", "Plot": "Select NHK content language"}
        ilist = self.addDir(color("Change Language", "yellow"), "CHANGE_LANG", ilist, "change_language", self.thumb, self.fanart, info)

        return ilist   
        
    # ========== CATEGORY LIST ==========
    
    def Categories(self, url, ilist):
        """Display categories"""
        try:
            data = requests.get(url, headers=self.defaultHeaders, timeout=10).json()
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Error", str(e), xbmcgui.NOTIFICATION_ERROR)
            return ilist
        if "/en/" in url:
            API_URL = API_BASE
        else:
            API_URL = API_BASE_LANG
        for cat in data.get("items", []):
            cat_name = cat["name"]
            cat_id = cat["id"]
            cat_thumb = self.thumb
            cat_fanart = self.fanart
            cat_api = f"{API_URL}/categories/{cat_id}/video_episodes"
            info = {
                "title": cat_name,
                "plot": f"Programs under category: {cat_name}",
                "mediatype": "tvshow",
            }
            ilist = self.addMenuItem(cat_name, "EPISODES_LIST", ilist, cat_api, cat_thumb, cat_fanart, info, isFolder=True)
        
        return ilist

    # ========== PROGRAM LIST ==========
    
    def ShowsList(self, url, ilist):
        """Display video programs in a category"""
        try:
            data = requests.get(url, headers=self.defaultHeaders, timeout=10).json()
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Error", str(e), xbmcgui.NOTIFICATION_ERROR)
            return ilist
        if "/en/" in url:
            API_URL = API_BASE
        else:
            API_URL = API_BASE_LANG
        for prog in data.get("items", []):
            pid = prog.get("id")
            title = prog.get("title").replace('\n', ' - ')
            desc = prog.get("description")
            thumb = NHK_BASE + prog["images"]["landscape"][1]["url"] if prog.get("images") else self.thumb
            fanart = NHK_BASE + prog["images"]["landscape"][-1]["url"] if prog.get("images") else self.fanart
            episodes_api = f"{API_URL}/video_programs/{pid}/video_episodes"
            total_video = prog.get("video_episodes",{})["total"]
            info = {
                "Title": title,
                "Plot": desc,
                "mediatype": "tvshow",
            }
            if total_video == 0:
                continue
            ilist = self.addMenuItem(color(title, 'steelblue'), "EPISODES_LIST", ilist, episodes_api, thumb, fanart, info, isFolder=True)

        # --- pagination link ---
        try:
            pagination = data.get("pagination", {})
            next_url = pagination.get("next")
            total = pagination.get("total")
            offset = pagination.get("offset")
            limit = pagination.get("limit")
            page = round(int(offset)/int(limit))+1
            total_page = round(int(total)/int(limit))+1
            thumb = "https://filedn.com/lXWPrdig44P7DGUkOEDrKLm/nhk/nextpage.jpg"
            if next_url:
                next_url = f'https://api.nhkworld.jp{pagination.get("next")}'
                ilist = self.addMenuItem(color(f">> Next Page {page+1}/{total_page}", "yellow"), "SHOWS_LIST", ilist, next_url, thumb, thumb, {"Title": "Next Page"}, isFolder=True)
        except:
            logs('No more page')
        
        return ilist

    # ========== EPISODE LIST ==========
    
    def EpisodesList(self, url, ilist): 
        """Display episodes for a given program"""
        try:
            data = requests.get(url, headers=self.defaultHeaders, timeout=10).json()
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Error", str(e), xbmcgui.NOTIFICATION_ERROR)
            return ilist

        for ep in data.get("items", []):
            show_title = ep.get('video_program')['title']
            title = f'{ep.get("title", "")}  '
            desc = ep.get("description", "")
            full_title = f"{title}{color(show_title, 'steelblue')}" if use_color=='true' else f"{title}({show_title})" 
            vid = ep.get("video", {})
            m3u8_url = vid.get("url")
            duration = vid.get("duration", 0)
            aired = ep.get("first_broadcasted_at")
            if aired:
                try:
                    aired = datetime.fromisoformat(aired.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    aired = ""
            thumb = NHK_BASE + ep["images"][1]["url"] if ep.get("images") else self.thumb
            fanart = NHK_BASE + ep["images"][-1]["url"] if ep.get("images") else self.fanart
            info = {
                "title": title,
                "plot": desc +"\n\nFirst Aired: "+ aired,
                "duration": duration,
                "studio": "NHK",
                "aired": aired,
                "FirstAired": aired,
                "mediatype": "episode",
            }
            li = xbmcgui.ListItem(label=full_title)
            li.setArt({"thumb": thumb, "fanart": fanart})
            li.setInfo("video", info)
            li.setProperty("IsPlayable", "true")

            show_id = ep.get('video_program')['id']

            # If there is show_id → create context menu “Open Show”
            if show_id:
                show_url = f"https://api.nhkworld.jp/showsapi/v1/en/video_programs/{show_id}/video_episodes"
                show_menu_url = f"{sys.argv[0]}?mode=EPISODES_LIST&url={urllib.parse.quote_plus(show_url)}"
                li.addContextMenuItems([
                    (f"Open Show: {show_title}", f'Container.Update({show_menu_url}, replace)')
                ])
            
            u = f"{sys.argv[0]}?mode=PLAY_EPISODE&url={urllib.parse.quote_plus(m3u8_url)}"
            ilist.append((u, li, False))

        # --- pagination link ---
        try:
            pagination = data.get("pagination", {})
            next_url = pagination.get("next")
            total = pagination.get("total")
            offset = pagination.get("offset")
            limit = pagination.get("limit")
            page = round(int(offset)/int(limit))+1
            total_page = round(int(total)/int(limit))+1
            thumb = "https://filedn.com/lXWPrdig44P7DGUkOEDrKLm/nhk/nextpage.jpg"
            if next_url:
                next_url = f'https://api.nhkworld.jp{pagination.get("next")}'
                ilist = self.addMenuItem(color(f">> Next Page {page+1}/{total_page}", "yellow"), "EPISODES_LIST", ilist, next_url, thumb, thumb, {"Title": "Next Page"}, isFolder=True)
        except:
            logs('No more page')
        
        return ilist

    def changeLanguageAndFont(self, url=None):
        """Select NHK content language and mark CJK with Arial font for list labels"""
        current_idx = int(addon.getSetting("language") or 0)
        idx = xbmcgui.Dialog().select("Select NHK Language", LANG_OPTIONS, preselect=current_idx)
        if idx == -1:
            return  

        lang_name = LANG_OPTIONS[idx]
        lang_code = LANG_MAP.get(lang_name, "en")
        addon.setSetting("language", str(idx))

        if lang_code in CJK_LANGS:
            import xml.etree.ElementTree as ET
            guisettings= xbmcvfs.translatePath('special://home/userdata/guisettings.xml')
            tree = ET.parse(guisettings)
            root = tree.getroot()

            for setting in root.iter('setting'):
                if setting.get('id') == "lookandfeel.font":
                    setting_font = setting.text
            
            #skin_font = xbmc.getInfoLabel("Skin.String(lookandfeel.font)") 
            if setting_font == "Default":
                text = "You need to change the font to suit the language (Arial font can support hieroglyphs)"
                xbmcgui.Dialog().notification(f'NHK World', text, xbmcgui.NOTIFICATION_INFO, 7000)

# ======== NEWS SECTION ========

    def NewsMenu(self, url, ilist):

        if url == "news_in_english":
            ilist = self.addDir("All News Videos", "NEWS_LIST", ilist, "ALL_en", self.thumb, self.fanart,
                                {"Title": "All News", "Plot": "All NHK World News videos"})
            ilist = self.addDir("Japan", "NEWS_LIST", ilist, "JAPAN_en", self.thumb, self.fanart)
            ilist = self.addDir("Asia", "NEWS_LIST", ilist, "ASIA_en", self.thumb, self.fanart)
            ilist = self.addDir("World", "NEWS_LIST", ilist, "WORLD_en", self.thumb, self.fanart)
            ilist = self.addDir("Business & Tech", "NEWS_LIST", ilist, "BIZTCH_en", self.thumb, self.fanart)

        else:
            ilist = self.addDir(ALL_NEW_VIDEOS, "NEWS_LIST", ilist, "ALL", self.thumb, self.fanart,
                                {"Title": "All News", "Plot": "All NHK World News videos"})
            ilist = self.addDir(JAPAN, "NEWS_LIST", ilist, "JAPAN", self.thumb, self.fanart)
            ilist = self.addDir(ASIA, "NEWS_LIST", ilist, "ASIA", self.thumb, self.fanart)
            ilist = self.addDir(WORLD, "NEWS_LIST", ilist, "WORLD", self.thumb, self.fanart)
            ilist = self.addDir(BUSINESS_TECH, "NEWS_LIST", ilist, "BIZTCH", self.thumb, self.fanart)
            ilist = self.addDir(SPECIAL_CLIPS, "NEWS_LIST", ilist, "CLIPS", self.thumb, self.fanart)

        return ilist
        
    def NewsList(self, url, ilist):
        
        def ilist_details(x, ilist):
            title = x.get("title") or "No title"
            page_url = "https://www3.nhk.or.jp" + x.get("page_url", "")
            thumb = "https://www3.nhk.or.jp" + x.get("thumbnails",{})["small"] 
            desc = x.get("description", "")
            updated_at = int(x.get("updated_at", ""))/1000
            if updated_at:
                try:
                    updated_at = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(updated_at))
                except Exception:
                    updated_at = ""
            info = {
                "Title": title,
                "Plot": desc  +'\n\nUpdated at: '+  updated_at,
                "studio": "NHK",
                "mediatype": "video",
            }
            ilist = self.addVideo(title, "PLAY_NEWS", ilist, page_url, thumb, self.addonFanart, info) 
       
        if "CLIPS" in url:
            if "CLIPS_en" in url:
                news_url = f"https://www3.nhk.or.jp/nhkworld/data/en/news/programs/special/video_list.json"
            else:
                news_url = f"https://www3.nhk.or.jp/nhkworld/data/{lang_code}/news/programs/special/video_list.json"
            data = requests.get(news_url, headers=self.defaultHeaders, timeout=10).json()
            items = data.get("data", [])
            for item in items:
                title = item.get("title") or "No title"
                thumbnail = item.get("thumbnail")
                thumb = NHK_BASE+ thumbnail
                url = NHK_BASE+ item.get("url")
                onair_date = item.get("onair_date")/1000
                m3u8_url = "https://vod-stream.nhk.jp/"+ thumbnail.replace("thumbnails", "medias").replace("_d","_").replace(".jpg", "_HQ/index.m3u8")
                info = {
                    "title": title,
                    "plot": "On Aried: "+   time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(onair_date)),
                    "studio": "NHK",
                    "mediatype": "video",
                }
                ilist = self.addEpisode(title, "PLAY_NEWS", ilist, m3u8_url, thumb, self.addonFanart, info)
            
            return ilist
            
        else:
            if "_en" in url:
                news_url = "https://www3.nhk.or.jp/nhkworld/data/en/news/all.json"
                category = url.replace("_en", "")
            else:
                news_url = f"https://www3.nhk.or.jp/nhkworld/data/{lang_code}/news/all.json"
                category = url
      
            try:
                data = requests.get(news_url, headers=self.defaultHeaders, timeout=10).json()
            except Exception as e:
                xbmcgui.Dialog().notification("NHK Error", str(e), xbmcgui.NOTIFICATION_ERROR)
                return ilist

            items = data.get("data", [])

            for x in items:
                categories = x.get("categories", {})['name']
                if not x.get("videos") :
                    continue
                
                """Display NHK News by category"""
                if category in categories and category != "ALL":
                    ilist_details(x, ilist)                

                elif category == "ALL":
                    ilist_details(x, ilist)                
            
            return ilist
        
    # ========== SCHEDULE ==========

    def ScheduleDays(self, url, ilist):

        JST = timezone(timedelta(hours=9))
        if time.daylight and time.localtime().tm_isdst:
            local_offset = -time.altzone // 3600
        else:
            local_offset = -time.timezone // 3600
        LOCAL = timezone(timedelta(hours=local_offset))

        # Get today's date for both local and Tokyo
        today_local = datetime.now(LOCAL).date()
        today_tokyo = datetime.now(JST).date()
        
        # If user chooses to view by Tokyo → Today will be JST
        today = today_tokyo if view_by_tokyo else today_local

        for offset in range(-days_past, days_future):
            day = today + timedelta(days=offset) 
            day_tokyo = today_tokyo + timedelta(days=offset) 
            json_file = day_tokyo.strftime('%Y%m%d.json')  # always get json in Japanese time
            label = day.strftime('%a, %b %d')

            if view_by_tokyo:
                label = (day - timedelta(hours=9)).strftime('%a, %b %d')

            if day == today:
                # label = f'[COLOR green]{label} (Today)[/COLOR]'
                # no more today in days list 
                continue
                
            if offset == 1:
                label = label + " (Tomorrow)"
            if offset == -1:
                label = label + " (Yesterday)"
                
            self.addDir(label, "SCHEDULE_ITEMS", ilist,
                        f"https://masterpl.hls.nhkworld.jp/epg/w/{json_file}",
                        "", self.addonFanart)
                        
        return ilist

    def ScheduleItems(self, url, ilist):
        index_offset = 0

        JST = timezone(timedelta(hours=9))
        if time.daylight and time.localtime().tm_isdst:
            local_offset = -time.altzone // 3600
        else:
            local_offset = -time.timezone // 3600
        LOCAL = timezone(timedelta(hours=local_offset))

        if url == "Today Schedule":
            self.ScheduleDays(url, ilist)
            
            index_offset = days_past + days_future 

            # Get today's date for both local and Tokyo
            today_local = datetime.now(LOCAL).date()
            today_tokyo = datetime.now(JST).date()

            # If user chooses to view by Tokyo → Today will be JST
            today = today_tokyo if view_by_tokyo else today_local
            today_json_file = today_tokyo.strftime('%Y%m%d.json')  # always get json in Japanese time
            url = f"https://masterpl.hls.nhkworld.jp/epg/w/{today_json_file}"

            ilist = self.addDir(color(f"--------------- Schedule for {today} ---------------", "yellow"), "SCHEDULE_ITEMS", ilist, "Today Schedule", self.thumb, self.fanart)
        
        try:
            data = requests.get(url, timeout=10).json()
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Live", f"Lỗi tải dữ liệu: {e}", xbmcgui.NOTIFICATION_ERROR)
            return ilist

        now_local = datetime.now(LOCAL)
        now_jst = datetime.now(JST)
        data = data["data"]
        live_index = None
        visible_index = 0  # actual location on UI (ilist)

        skip_counts = {"missing_time": 0, "info": 0, "vod_unavailable": 0}
        for prog in data:
            
            if not prog.get("startTime") or not prog.get("endTime"):
                skip_counts["missing_time"] += 1
                continue
            if prog.get("title") == "INFO":
                skip_counts["info"] += 1
                continue
            
            start_jst = datetime.fromisoformat(prog["startTime"].replace('Z', '+09:00')).astimezone(JST)
            end_jst = datetime.fromisoformat(prog["endTime"].replace('Z', '+09:00')).astimezone(JST)
            start_local = start_jst.astimezone(LOCAL)
            end_local = end_jst.astimezone(LOCAL)

            if end_jst < now_jst and prog.get("vodFlag") == 0:
                skip_counts["vod_unavailable"] += 1
                continue
            
            if index_offset > 0:
                label_time = f'{start_jst.strftime("%I:%M %p")}' if view_by_tokyo else f'{start_local.strftime("%I:%M %p")}'
            else:
                label_time = f'{start_jst.strftime("%b %d  %I:%M %p")}' if view_by_tokyo else f'{start_local.strftime("%b %d  %I:%M %p")}'
                    
            C = 'lightgrey'
            livenow = ""
            
            if end_jst < now_jst:
                C = 'lightgreen'
                if prog.get("vodFlag") == 0:
                    continue
            elif start_jst <= now_jst <= end_jst:
                C = 'yellow'
                livenow = color("[B]LIVE NOW:[/B] ", "red")
                live_index = visible_index  # <-- Index on UI!
                
            title = prog.get("title", "").strip()
            episode = prog.get("episodeTitle", "").strip()
            if episode:
                title_full = f"{episode}  [COLOR steelblue]{title}[/COLOR]"
            else:
                title_full = f"[COLOR red]{title}[/COLOR]"

            label = f'[COLOR {C}]{label_time}[/COLOR]  {title_full}'

            thumb = prog.get("episodeThumbnailURL") or prog.get("thumbnail") \
                    or "https://filedn.com/lXWPrdig44P7DGUkOEDrKLm/nhk/nhk_newsline.jpg"
            desc = prog.get("description", "")
            info = {
                "title": title_full,
                "plot": livenow + desc,
                "studio": "NHK",
                "mediatype": "video",
            }

            m3u8_url = prog.get("playURL", "")

            li = xbmcgui.ListItem(label=label)
            li.setArt({"thumb": thumb, "fanart": thumb})
            li.setInfo("video", info)
            li.setProperty("IsPlayable", "true")

            show_link = prog.get("link", "")
            show_id = ""
            if show_link:
                match = re.search(r'/shows/([^/]+)/', show_link)
                if match:
                    show_id = match.group(1)

            # If there is show_id → create context menu “Open Show”
            if show_id:
                show_url = f"https://api.nhkworld.jp/showsapi/v1/en/video_programs/{show_id}/video_episodes"
                show_menu_url = f"{sys.argv[0]}?mode=EPISODES_LIST&url={urllib.parse.quote_plus(show_url)}"
                li.addContextMenuItems([
                    (f"Open Show: {title}", f'Container.Update({show_menu_url}, replace)')
                ])
            
            u = f"{sys.argv[0]}?mode=PLAY_EPISODE&url={urllib.parse.quote_plus(m3u8_url)}"
            ilist.append((u, li, False))
            visible_index += 1

        try:
            logs(f"Skipped: {skip_counts}, live_index_on_UI={live_index}")
        except: pass
        
        if live_index:
            live_index = live_index+index_offset
        else:
            live_index = index_offset
        return ilist, live_index

    # ========== PLAY VIDEO ==========
    
    def PlayEpisode(self, params):
        params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
        url = params.get("url")
        if not url:
            xbmcgui.Dialog().notification("NHK Live", "Invalid stream URL.", xbmcgui.NOTIFICATION_ERROR, 3000)
            return

        url_1080 = url.replace("/master.m3u8", "/o-master.m3u8")
        test = requests.head(url_1080, headers=self.defaultHeaders, timeout=5, allow_redirects=True)
        if test.status_code == 200: 
            url = url_1080
                
        try:
            test = requests.head(url, headers=self.defaultHeaders, timeout=5, allow_redirects=True) #Check again for links that are not yet live in the schedule
            if test.status_code == 200: 
                liz = xbmcgui.ListItem(path=url, offscreen=True)
                liz.setProperty("inputstream", "inputstream.adaptive")
                liz.setMimeType("application/x-mpegURL")
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
            else:
                xbmcgui.Dialog().notification(
                    "NHK Live",
                    "This program is not yet available.",
                    xbmcgui.NOTIFICATION_INFO,
                    3000
                )
                return
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Live", f"Connection error: {e}", xbmcgui.NOTIFICATION_ERROR, 3000)
            return

    def PlayNews(self, url):
        if ".m3u8" in url:
            m3u8_url = url
            
        elif "/en/" in url:
            try:
                html = requests.get(url, timeout=10).text
                m3u8_url = xsearch('"contentUrl": "(.*?)"', html)
            except Exception as e:
                xbmcgui.Dialog().notification("NHK Error", "There are no videos for this content")
                return ilist
        else:
            html = requests.get(url, timeout=10).text
            key = xsearch(r'/news/(.*?)_L.jpg">', html)
            m3u8_url = f"https://vod-stream.nhk.jp/nhkworld/upld/medias/{lang_code}/news/{key}_HQ/index.m3u8"
 
        try:
            m3u8_720 = m3u8_url.replace("_HQ/index.m3u8", "_2M/index.m3u8")
            test = requests.head(m3u8_720, headers=self.defaultHeaders, timeout=5)
            if test.status_code == 200:
                m3u8_url = m3u8_720
        except Exception as e:
            logs(f"720p link failed: {e}")
            
        liz = xbmcgui.ListItem(path=m3u8_url, offscreen=True)
        liz.setProperty("inputstream", "inputstream.adaptive")
        liz.setMimeType("application/x-mpegURL")
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
