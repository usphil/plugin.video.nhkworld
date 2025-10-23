# -*- coding: utf-8 -*-
import sys, xbmc, xbmcgui, xbmcplugin, xbmcaddon, urllib.parse

class myAddon(object):
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.addonName = self.addon.getAddonInfo('name')
        self.addonIcon = self.addon.getAddonInfo('icon')
        self.addonFanart = self.addon.getAddonInfo('fanart')
        self.defaultHeaders = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36'
        }
    
    def addMenuItem(self, name, mode, ilist, url, icon, fanart, infoLabels=None, isFolder=True):
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
        if icon: li.setArt({'thumb': icon, 'icon': icon, 'poster': icon})
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
        
    def addEpisode(self, name, mode, ilist, url, img, fanart, infoLabels=None):
        u = f"{sys.argv[0]}?mode={mode}&url={urllib.parse.quote(str(url), safe='')}"
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

    def endDirectory(self, ilist):
        xbmcplugin.addDirectoryItems(int(sys.argv[1]), ilist, len(ilist))
        xbmcplugin.setContent(int(sys.argv[1]), 'videos')
        xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)

    def procDir(self, func, url, ctype):
        ilist = []
        ilist = func(url, ilist)
        if ilist is None:
            ilist = []
        self.endDirectory(ilist)

    def processAddonEvent(self):
        mtable = {
            None: [self.getAddonMenu, 'files'],
            'GC': [self.getAddonCats, 'files'],
            'GE': [self.getAddonEpisodes, 'episodes'],
            'SE': [self.getAddonSearch, 'files'],
            'GS': [self.getAddonShows, 'tvshows'],
            'SR': [self.getSearchResult, 'videos'],
            'NM': [self.getNewsMenu, 'files'],
            'NC': [self.get_news, 'videos'],
        }
        ftable = {
            'NT': self.get_PlayNews,
            'GV': self.get_PlayEpisode,
            'CL': self.changeLanguageAndFont,
            'DF': self.doFunction
        }
        parms = {}
        if len((sys.argv[2][1:])) > 0:
            parms = dict(arg.split("=") for arg in ((sys.argv[2][1:]).split("&")))
            for key in parms:
                parms[key] = urllib.parse.unquote_plus(parms[key])
        fun = mtable.get(parms.get('mode'))
        if fun:
            self.procDir(fun[0], parms.get('url',''), fun[1])
        else:
            fun = ftable.get(parms.get('mode'))
            if fun:
                fun(parms.get('url'))

    # Placeholder functions (addon implements these)
    def getAddonMenu(self, url, ilist): return ilist
    def getAddonCats(self, url, ilist): return ilist
    def getAddonEpisodes(self, url, ilist): return ilist
    def getAddonShows(self, url, ilist): return ilist
    def getNewsMenu(self, url, ilist): return ilist
    def get_news(self, url, ilist): return ilist
    def get_PlayNews(self, url): pass
    def get_PlayEpisode(self, url): pass
    def changeLanguageAndFont(self,url): pass
    def doFunction(self, url): pass
    def getAddonSearch(self, url, ilist): return ilist
    def getSearchResult(self, url, ilist): return ilist
