# -*- coding: utf-8 -*-
import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon, re, urllib.parse

class myAddon(object):
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addonName = self.addon.getAddonInfo('name')
        self.addonIcon = self.addon.getAddonInfo('icon')
        self.addonFanart = self.addon.getAddonInfo('fanart')
        self.defaultHeaders = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36'
        }
    
    def addMenuItem(self, name, mode, ilist, url, img, fanart, infoLabels=None, isFolder=True):
        li = xbmcgui.ListItem(label=name)
        if infoLabels:
            tag = li.getVideoInfoTag()
            if 'Title' in infoLabels: tag.setTitle(infoLabels['Title'])
            if 'Plot' in infoLabels: tag.setPlot(infoLabels['Plot'])
            if 'genre' in infoLabels: tag.setGenre(infoLabels['genre'])
            if 'duration' in infoLabels:
                dur = infoLabels['duration']
                dur_val = 0
                if isinstance(dur, (int, float)):
                    dur_val = int(dur)
                elif isinstance(dur, str):
                    if dur.startswith("PT"): 
                        import re
                        m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur)
                        if m:
                            h = int(m.group(1) or 0)
                            m_ = int(m.group(2) or 0)
                            s = int(m.group(3) or 0)
                            dur_val = h * 3600 + m_ * 60 + s
                    else:
                        try:
                            dur_val = int(float(dur))
                        except Exception:
                            dur_val = 0
                try:
                    tag.setDuration(dur_val)
                except Exception:
                    pass

            if 'studio' in infoLabels:
                studio_value = infoLabels['studio']
                try:
                    tag.setStudio(studio_value)  # Kodi 20
                except AttributeError:
                    try:
                        tag.setStudios([studio_value])  # Kodi 21+
                    except Exception:
                        pass

            if 'mediatype' in infoLabels: tag.setMediaType(infoLabels['mediatype'])
        if img: li.setArt({'thumb': img, 'icon': img, 'poster': img})
        if fanart: li.setArt({'fanart': fanart})
        u = f"{sys.argv[0]}?mode={mode}&url={urllib.parse.quote(str(url), safe='')}"

        ilist.append((u, li, isFolder))
        return ilist

    def addDir(self, name, mode, ilist, url, img, fanart, infoLabels=None):
        return self.addMenuItem(name, mode, ilist, url, img, fanart, infoLabels, True)

    def addVideo(self, name, mode, ilist, url, thumb, fanart, infoLabels):
        u = f"{sys.argv[0]}?mode={mode}&url={urllib.parse.quote(str(url), safe='')}"
        liz = xbmcgui.ListItem(label=name, path=url)
        liz.setProperty("IsPlayable", "true")
        liz.setArt({'thumb': thumb})
        tag = liz.getVideoInfoTag()
        if infoLabels:
            if 'Title' in infoLabels: tag.setTitle(infoLabels['Title'])
            if 'Plot' in infoLabels: tag.setPlot(infoLabels['Plot'])
        isFolder = False
        ilist.append((u, liz, isFolder))
        return ilist
        
    def addEpisode(self, name, mode, ilist, url, img, fanart, infoLabels=None, extra=None):
        query = {"mode": mode, "url": url}
        if extra:
            query.update(extra)
        u = sys.argv[0] + "?" + urllib.parse.urlencode(query)
        liz = xbmcgui.ListItem(label=name, path=url)
        liz.setProperty("IsPlayable", "true")
        liz.setArt({'thumb': img, 'icon': img, 'fanart': fanart})
        tag = liz.getVideoInfoTag()
        if infoLabels:
            if 'title' in infoLabels:
                tag.setTitle(infoLabels['title'])
            if 'plot' in infoLabels:
                tag.setPlot(infoLabels['plot'])
            if 'duration' in infoLabels:
                try:
                    tag.setDuration(int(float(infoLabels['duration'])))
                except:
                    pass
        isFolder = False
        ilist.append((u, liz, isFolder))
        return ilist

    def endDirectory(self, ilist, live_index=None):
        handle = int(sys.argv[1])
        xbmcplugin.addDirectoryItems(handle, ilist, len(ilist))
        xbmcplugin.setContent(handle, 'videos')
        xbmcplugin.endOfDirectory(handle, cacheToDisc=False)

        if live_index is not None:
            ADDON = self.addon

            view_mode_label = ADDON.getSetting("view_mode")
            match = re.search(r'\((\d+)\)', view_mode_label)
            container_id = int(match.group(1)) if match else 50

            custom_id = ADDON.getSetting("custom_view_mode")
            if custom_id.strip() != "0":
                container_id = int(custom_id)
               
            try:
                xbmc.sleep(600)
                xbmc.executebuiltin(f'Control.SetFocus({container_id}, {live_index}, absolute)')
            except Exception as e:
                xbmc.log(f"[NHK] Focus move failed: {e}", xbmc.LOGERROR)
                
        # xbmc.executebuiltin('Container.SetViewMode(516)')  # for Titan Skin

    def procDir(self, func, url, ctype):
        ilist = []
        result = func(url, ilist)

        # If func return tuple (ilist, live_index)
        if isinstance(result, tuple):
            ilist, live_index = result
        else:
            ilist = result
            live_index = None

        if ilist is None:
            ilist = []

        self.endDirectory(ilist, live_index)

    def processAddonEvent(self):
        mtable = {
            None: [self.MainMenu, 'files'],
            'CATEGORIES': [self.Categories, 'files'],
            'EPISODES_LIST': [self.EpisodesList, 'episodes'],
            'SHOWS_LIST': [self.ShowsList, 'tvshows'],
            'SEARCH_NEWS_RESULT': [self.SearchNewsResult, 'videos'],
            'SEARCH_SHOWS_RESULT': [self.SearchShowsResult, 'videos'],
            'SEARCH_ALL': [self.SearchAll, 'file'],
            'SEARCH_HUB': [self.SearchHub, 'files'],
            'SEARCH_ALL_KEYBOARD': [self.SearchKeyboard, 'files'],
            'SEARCH_ALL_MENU': [self.SearchAllMenu, 'files'],
            'NEWS_MENU': [self.NewsMenu, 'files'],
            'NEWS_LIST': [self.NewsList, 'videos'],
            'SCHEDULE_DAYS': [self.ScheduleDays, 'files'],
            'SCHEDULE_ITEMS': [self.ScheduleItems, 'files'],
            'SECOND_LANG': [self.SecondLang, 'files'],
            'CLEAR_HISTORY': [self.ClearHistory, 'files'],
            'DELETE_KEYWORD': [self.DeleteKeyword, 'files'],
        }
        ftable = {
            'PLAY_NEWS': self.PlayNews,
            'PLAY_EPISODE': self.PlayEpisode,
            'CHANGE_LANG': self.changeLanguageAndFont,
            'OPEN_SETTINGS': self.openSettings,
        }
        parms = {}
        
        if len((sys.argv[2][1:])) > 0:
            parms = dict(arg.split("=") for arg in ((sys.argv[2][1:]).split("&")))
            for key in parms:
                parms[key] = urllib.parse.unquote_plus(parms[key])

        mode = parms.get('mode')
        fun = mtable.get(mode)
        
        if mode is None:
            self._search_active = False
            
        if fun:
            self.procDir(fun[0], parms.get('url',''), fun[1])
        else:
            fun = ftable.get(mode)
            if fun:
                fun(parms.get('url'))

    # Placeholder functions (addon implements these)
    def MainMenu(self, url, ilist): return ilist
    def Categories(self, url, ilist): return ilist
    def EpisodesList(self, url, ilist): return ilist
    def ShowsList(self, url, ilist): return ilist
    def NewsMenu(self, url, ilist): return ilist
    def NewsList(self, url, ilist): return ilist
    def ScheduleDays(self, url, ilist): return ilist
    def ScheduleItems(self, url, ilist): return ilist
    def PlayNews(self, url): pass
    def PlayEpisode(self, params): pass
    def ClearHistory(self, url, ilist): return ilist
    def changeLanguageAndFont(self,url): pass
    def SearchShows(self, url, ilist): return ilist
    def SearchAllMenu(self, url, ilist): return ilist
    def SearchHub(self, url, ilist): return ilist
    def SearchKeyboard(self, url, ilist): return ilist
    def SearchAll(self, url, ilist): return ilist
    def SearchNewsResult(self, url, ilist): return ilist
    def SearchShowsResult(self, url, ilist): return ilist
    def SecondLang(self, url, ilist): return ilist
