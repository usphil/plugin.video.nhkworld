# -*- coding: utf-8 -*-
from resources.lib import helper
from resources.lib.dict import LANG_OPTIONS, LANG_MAP, CJK_LANGS, _, get_lang_code
import requests, datetime, time, json, re, urllib.parse
import sys, xbmc, xbmcvfs, xbmcplugin, xbmcaddon, xbmcgui
    
NHK_BASE = "https://www3.nhk.or.jp"
API_BASE = "https://api.nhkworld.jp/showsapi/v1/en"
addon = xbmcaddon.Addon()
lang_code = get_lang_code(addon)
API_BASE_LANG = f"https://api.nhkworld.jp/showsapi/v1/{lang_code}"

CAT = _("Categories", lang_code)
LATEST_VID = _("Latest_Videos", lang_code)
LATEST_SHOWS = _("Latest_Shows", lang_code)
TREN= _("Trending", lang_code)
PLOT_CAT = _("Plot_cat", lang_code)
PLOT_VID = _("Plot_vid", lang_code)
PLOT_SHOW = _("Plot_show", lang_code)
use_color = addon.getSetting('usecolor')

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

    def getAddonSearch(self, url, ilist):
        """
        Phase 1: Ask user for keyword, then redirect to result mode (SR)
        """
        kb = xbmc.Keyboard('', 'Enter search keyword')
        kb.doModal()
        if not kb.isConfirmed():
            return ilist
        keyword = kb.getText().strip()
        if not keyword:
            return ilist

        q = urllib.parse.quote_plus(keyword)
        next_url = f"https://api.nhkworld.jp/nwapi/search/nhkworld@en@news/0/30/{q}/list.json"
        ilist = self.addMenuItem(
            f"Search results for: {keyword}",
            "SR", 
            ilist,
            next_url,
            self.addonIcon,
            self.addonFanart,
            {"Title": keyword, "Plot": "Search results"},
            isFolder=True
        )
        return ilist

    def getSearchResult(self, url, ilist):
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

            if link.startswith("/"):
                link = "https://www3.nhk.or.jp" + link
            if thumb.startswith("/"):
                thumb = "https://www3.nhk.or.jp" + thumb

            m3u8_url = None
            try:
                html = requests.get(link, headers=self.defaultHeaders, timeout=10).text
                for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S):
                    jtxt = m.group(1).strip()
                    if '"VideoObject"' in jtxt:
                        try:
                            j = json.loads(jtxt)
                            m3u8_url = j.get("contentUrl")
                            if m3u8_url:
                                break
                        except Exception:
                            pass
            except Exception:
                pass

            if not m3u8_url:
                continue  

            info = {
                "title": title,
                "plot": desc,
                "duration": duration,
                "studio": "NHK World",
                "mediatype": "video"
            }
            ilist = self.addEpisode(title, "GV", ilist, m3u8_url, thumb, thumb, info)

        return ilist

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
                logs(f"Using 1080p live stream: {primary_url}")
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

    def getAddonMenu(self, url, ilist):
        img = self.addonIcon
        fanart = self.addonFanart

        info = {"Title": "Search", "Plot": "Search NHK World News & Videos"}
        ilist = self.addDir(color("Search", "red"), "SE", ilist, "search", img, fanart, info)
        
        live_url = self.get_live_stream()
        info = {"Title": "NHK World Live", "Plot": "Watch NHK World live stream"}
        ilist = self.addVideo(color("Live Now", "green"), "GV", ilist, live_url, img, fanart, info)

        info = {"Title": "News", "Plot": "NHK World latest news videos"}
        ilist = self.addDir("NHK News", "NM", ilist, "news", img, fanart, info)

        programs_url = f"{API_BASE}/video_programs?limit=100&sort=-date"
        info = {"Title": "Video Programs", "Plot": "Browse NHK World on-demand video programs"}
        ilist = self.addDir(color("Latest Shows","orange"), "GS", ilist, programs_url, img, fanart, info)

        programs_url = f"{API_BASE}/video_programs?limit=10&sort=trending"
        info = {"Title": "Video Programs", "Plot": "Browse NHK World trending programs"}
        ilist = self.addDir(color("Trending","orange"), "GS", ilist, programs_url, img, fanart, info)

        videos_url = f"{API_BASE}/video_episodes?limit=100&offset=0"
        info = {"Title": "Latest Videos", "Plot": "Browse NHK World on-demand latest videos"}
        ilist = self.addDir(color("Latest Videos", "orange"), "GE", ilist, videos_url, img, fanart, info)

        cat_url = f"{API_BASE}/categories/"
        info = {"Title": "Categories", "Plot": "Explore NHK World programs by category"}
        ilist = self.addDir(color("Categories", "orange"), "GC", ilist, cat_url, img, fanart, info)

        ilist = self.addDir("---> The items below are for some other languages.", "", ilist, "", img, fanart)

        programs_url = f"{API_BASE_LANG}/video_programs?limit=100&sort=-date"
        info = {"Title": LATEST_SHOWS, "Plot": PLOT_SHOW}
        ilist = self.addDir(color(LATEST_SHOWS,"cyan"), "GS", ilist, programs_url, img, fanart, info)

        videos_url = f"{API_BASE_LANG}/video_episodes?limit=100&offset=0"
        info = {"Title": LATEST_VID, "Plot": PLOT_VID}
        ilist = self.addDir(color(LATEST_VID, "cyan"), "GE", ilist, videos_url, img, fanart, info)

        cat_url = f"{API_BASE_LANG}/categories/"
        info = {"Title": CAT, "Plot": PLOT_CAT}
        ilist = self.addDir(color(CAT, "cyan"), "GC", ilist, cat_url, img, fanart, info)

        info = {"Title": "Change Language", "Plot": "Select NHK content language"}
        ilist = self.addDir(color("Change Language", "yellow"), "CL", ilist, "change_language", img, fanart, info)

        return ilist

    # ========== CATEGORY LIST ==========
    def getAddonCats(self, url, ilist):
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
            cat_thumb = self.addonIcon
            cat_fanart = self.addonFanart
            cat_api = f"{API_URL}/categories/{cat_id}/video_episodes"
            info = {
                "title": cat_name,
                "plot": f"Programs under category: {cat_name}",
                "mediatype": "tvshow",
            }
            ilist = self.addMenuItem(cat_name, "GE", ilist, cat_api, cat_thumb, cat_fanart, info, isFolder=True)
        return ilist


    # ========== PROGRAM LIST ==========
    def getAddonShows(self, url, ilist):
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
            thumb = NHK_BASE + prog["images"]["landscape"][1]["url"] if prog.get("images") else self.addonIcon
            fanart = NHK_BASE + prog["images"]["landscape"][-1]["url"] if prog.get("images") else self.addonFanart
            episodes_api = f"{API_URL}/video_programs/{pid}/video_episodes"
            total_video = prog.get("video_episodes",{})["total"]
            info = {
                "Title": title,
                "Plot": desc,
                "mediatype": "tvshow",
            }
            if total_video == 0:
                continue
            ilist = self.addMenuItem(title, "GE", ilist, episodes_api, thumb, fanart, info, isFolder=True)

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
                ilist = self.addMenuItem(color(f">> Next Page {page+1}/{total_page}", "yellow"), "GS", ilist, next_url, thumb, fanart, {"Title": "Next Page"}, isFolder=True)
        except:
            logs('No more page')
            
        return ilist


    # ========== EPISODE LIST ==========
    def getAddonEpisodes(self, url, ilist):
        """Display episodes for a given program"""
        try:
            data = requests.get(url, headers=self.defaultHeaders, timeout=10).json()
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Error", str(e), xbmcgui.NOTIFICATION_ERROR)
            return ilist

        for ep in data.get("items", []):
            title = ep.get("title")
            if not title:
                title = ep['video_program']['title']
            desc = ep.get("description", "")
            vid = ep.get("video", {})
            m3u8_url = vid.get("url")
            duration = vid.get("duration", 0)
            aired = ep.get("first_broadcasted_at")
            if aired:
                try:
                    aired = datetime.datetime.fromisoformat(aired.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                except Exception:
                    aired = ""
            thumb = NHK_BASE + ep["images"][1]["url"] if ep.get("images") else self.addonIcon
            fanart = NHK_BASE + ep["images"][-1]["url"] if ep.get("images") else self.addonFanart
            info = {
                "title": title,
                "plot": desc +"\n\nFirst Aired: "+ aired,
                "duration": duration,
                "studio": "NHK",
                "aired": aired,
                "FirstAired": aired,
                "mediatype": "episode",
            }
            ilist = self.addEpisode(title, "GV", ilist, m3u8_url, thumb, fanart, info)

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
                ilist = self.addMenuItem(color(f">> Next Page {page+1}/{total_page}", "yellow"), "GS", ilist, next_url, thumb, fanart, {"Title": "Next Page"}, isFolder=True)
        except:
            logs('No more page')
            
        return ilist

    def changeLanguageAndFont(self, url=None):
        """Select NHK content language and mark CJK with Arial font for list labels"""
        addon = xbmcaddon.Addon()
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

    def getNewsMenu(self, url, ilist):
        logs("getNewsMenu() CALLED")

        img = self.addonIcon
        fanart = self.addonFanart

        ilist = self.addDir("All News Videos", "NC", ilist, "ALL", img, fanart,
                            {"Title": "All News", "Plot": "All NHK World News videos"})
        ilist = self.addDir("Japan", "NC", ilist, "JAPAN", img, fanart)
        ilist = self.addDir("Asia", "NC", ilist, "ASIA", img, fanart)
        ilist = self.addDir("World", "NC", ilist, "WORLD", img, fanart)
        ilist = self.addDir("Business & Tech", "NC", ilist, "BIZTCH", img, fanart)

        return ilist
        
    def get_news(self, url, ilist):
        
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
                "Plot": desc  +'\nUpdated At: '+  updated_at,
                "studio": "NHK",
                "mediatype": "video",
            }
            ilist = self.addVideo(title, "NT", ilist, page_url, thumb, self.addonFanart, info) 

        logs(f"DEBUG get_news() called with url={url}")
        category = url.upper() if url else "ALL"
        logs(f"MODE NC received URL={category}")

        news_url = "https://www3.nhk.or.jp/nhkworld/data/en/news/all.json"
        try:
            data = requests.get(news_url, headers=self.defaultHeaders, timeout=10).json()
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Error", str(e), xbmcgui.NOTIFICATION_ERROR)
            return ilist

        items = data.get("data", [])
        logs(f"Total news items loaded: {len(items)}")

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
        
    # ========== PLAY VIDEO ==========
    
    def get_PlayEpisode(self, url):
        
        """Play .m3u8 stream"""
        liz = xbmcgui.ListItem(path=url, offscreen=True)
        liz.setProperty("inputstream", "inputstream.adaptive")
        liz.setMimeType("application/x-mpegURL")
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
        
    def get_PlayNews(self, url):
        """Play the selected NHK News video"""
        logs(f"Parsing top news video page: {url}\n\n")
        try:
            html = requests.get(url, timeout=10).text
            m3u8_url = xsearch('"contentUrl": "(.*?)"', html)
        except Exception as e:
            xbmcgui.Dialog().notification("NHK Error", "There are no videos for this content")
            return ilist

        try:
            test = requests.head(m3u8_url.replace("_HQ/index.m3u8", "_2M/index.m3u8"), headers=self.defaultHeaders, timeout=5)
            if test.status_code == 200:
                m3u8_url = m3u8_url.replace("_HQ/index.m3u8", "_2M/index.m3u8")
        except Exception as e:
            logs(f"720p link failed: {e}")

        liz = xbmcgui.ListItem(path=m3u8_url, offscreen=True)
        liz.setProperty("inputstream", "inputstream.adaptive")
        liz.setMimeType("application/x-mpegURL")
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
