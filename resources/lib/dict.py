# -*- coding: utf-8 -*-
import xbmcaddon

CJK_LANGS = ["ja", "zh", "zt", "ko", "ar", "th", "my", "hi"]

LANG_OPTIONS = [
    "English",
    "日本語 (Japanese)",
    "中文（简体）(Chinese Simplified)",
    "中文（繁體）(Chinese Traditional)",
    "हिन्दी (Hindi)",
    "العربية (Arabic)",
    "ภาษาไทย (Thai)",
    "မြန်မာဘာသာစကား (Burmese)",
    "Español (Spanish)",
    "Français (French)",
    "Русский (Russian)",
    "Português (Portuguese)",
    "한국어 (Korean)",
    "Українська (Ukrainian)",
    "Bahasa Indonesia (Indonesian)",
    "Türkçe (Turkey)",
    "Tiếng Việt (Vietnamese)"
]

LANG_MAP = {
    "English": "en",
    "日本語 (Japanese)": "ja",
    "中文（简体）(Chinese Simplified)": "zh",
    "中文（繁體）(Chinese Traditional)": "zt",
    "العربية (Arabic)": "ar",
    "हिन्दी (Hindi)": "hi",
    "ภาษาไทย (Thai)": "th",
    "မြန်မာဘာသာစကား (Burmese)": "my",
    "Español (Spanish)": "es",
    "Français (French)": "fr",
    "Русский (Russian)": "ru",
    "Português (Portuguese)": "pt",
    "한국어 (Korean)": "ko",
    "Українська (Ukrainian)": "uk",
    "Bahasa Indonesia (Indonesian)": "id",
    "Türkçe (Turkey)": "tr",
    "Tiếng Việt (Vietnamese)": "vi"
}

UI_STRINGS = {
    "Latest Shows": {
        "en": "Latest Shows",
        "ja": "最新の番組",
        "zh": "最新节目",
        "zt": "最新節目",
        "ko": "최신 쇼",
        "es": "Últimos programas",
        "fr": "Derniers spectacles",
        "pt": "Últimos Shows",
        "ru": "Последние шоу",
        "uk": "Останні шоу",
        "ar": "أحدث العروض",
        "hi": "नवीनतम शो",
        "th": "รายการล่าสุด",
        "my": "နောက်ဆုံးထွက်ရှိုးများ",
        "id": "Acara Terbaru",
        "tr": "Son Gösteriler",
        "vi": "Chương trình mới nhất"
    },
    "Trending": {
        "en": "Trending",
        "ja": "トレンド",
        "zh": "热门内容",
        "zt": "熱門內容",
        "ko": "트렌드",
        "es": "Tendencias",
        "fr": "Tendance",
        "pt": "Tendências",
        "ru": "В тренде",
        "uk": "Тренди",
        "ar": "الأكثر رواجًا",
        "hi": "रुझान",
        "th": "กำลังเป็นที่นิยม",
        "my": "ခေတ်စားနေသည်။",
        "id": "Sedang tren",
        "tr": "Trend olan",
        "vi": "Xu hướng"
    },
    "Latest Videos": {
        "en": "Latest Videos",
        "ja": "最新動画",
        "zh": "最新视频",
        "zt": "最新影片",
        "ko": "최신 동영상",
        "es": "Videos Recientes",
        "fr": "Dernières vidéos",
        "pt": "Últimos Vídeos",
        "ru": "Последние видео",
        "uk": "Найновіші відео",
        "ar": "أحدث الفيديوهات",
        "hi": "नवीनतम वीडियो",
        "th": "วิดีโอล่าสุด",
        "my": "နောက်ဆုံးဗီဒီယိုများ",
        "id": "Video Terbaru",
        "tr": "Son Videolar",
        "vi": "Video Mới Nhất"
    },
    "Categories": {
        "en": "Categories",
        "ja": "カテゴリー",
        "zh": "分类",
        "zt": "分類",
        "ko": "카테고리",
        "es": "Categorías",
        "fr": "Catégories",
        "pt": "Categorias",
        "ru": "Категории",
        "ar": "الفئات",
        "hi": "श्रेणियाँ",
        "th": "หมวดหมู่",
        "my": "အမျိုးအစားများ",
        "id": "Kategori",
        "tr": "Kategoriler",
        "uk": "Категорії",
        "vi":"Thể Loại"
    },
    "Category Plot": {
        "en": "Explore NHK World programs by category",
        "ja": "NHKワールドの番組をカテゴリー別に探す",
        "zh": "按类别浏览 NHK World 节目",
        "zt": "按類別瀏覽 NHK World 節目",
        "ko": "카테고리별 NHK World 프로그램 탐색",
        "es": "Explora los programas de NHK World por categoría",
        "fr": "Explorez les programmes de NHK World par catégorie",
        "pt": "Explore os programas NHK World por categoria",
        "ru": "Изучите программы NHK World по категориям",
        "ar": "استكشف برامج NHK World حسب الفئة",
        "hi": "एनएचके वर्ल्ड कार्यक्रमों को श्रेणी के अनुसार देखें",
        "th": "สำรวจรายการ NHK World ตามหมวดหมู่",
        "my": "အမျိုးအစားအလိုက် NHK World အစီအစဉ်များကို စူးစမ်းပါ။",
        "id": "Jelajahi program NHK World berdasarkan kategori",
        "tr": "카테고리별 NHK World 프로그램 탐색",
        "uk": "Ознайомтеся з програмами NHK World за категоріями",
        "vi":"Khám phá các chương trình của NHK World theo thể loại"
    },
    "Video Plot": {
        "en": "Browse NHK World on-demand latest videos",
        "ja": "NHKワールドオンデマンドの最新動画を閲覧",
        "zh": "浏览 NHK World 点播最新视频",
        "zt": "瀏覽 NHK World 點播最新視頻",
        "ko": "NHK World 온디맨드 최신 영상 보기",
        "es": "Explora los últimos videos a pedido de NHK World",
        "fr": "Parcourez les dernières vidéos à la demande de NHK World",
        "pt": "Navegue pelos vídeos mais recentes do NHK World on-demand",
        "ru": "Просмотрите последние видео NHK World по запросу",
        "ar": "تصفح أحدث مقاطع الفيديو حسب الطلب لقناة NHK World",
        "hi": "एनएचके वर्ल्ड के नवीनतम वीडियो ऑन-डिमांड ब्राउज़ करें",
        "th": "เรียกดูวิดีโอล่าสุดตามต้องการของ NHK World",
        "my": "NHK World တွင် လိုအပ်သလောက် နောက်ဆုံးထွက် ဗီဒီယိုများကို ကြည့်ပါ။",
        "id": "Telusuri video terbaru NHK World sesuai permintaan",
        "tr": "NHK World'ün isteğe bağlı en son videolarına göz atın",
        "uk": "Перегляньте найновіші відео NHK World на вимогу",
        "vi":"Duyệt các video mới nhất của NHK World"
    },
    "Show Plot": {
        "en": "Browse NHK World latest shows",
        "ja": "NHKワールドの最新番組を閲覧",
        "zh": "浏览 NHK World 的最新节目",
        "zt": "瀏覽 NHK World 的最新節目",
        "ko": "NHK World 최신 프로그램 탐색",
        "es": "Explora los últimos programas de NHK World",
        "fr": "Parcourir les dernières émissions de NHK World",
        "pt": "Parcourir les dernières émissions de NHK World",
        "ru": "Просмотрите последние шоу NHK World",
        "ar": "تصفح أحدث عروض NHK World",
        "hi": "एनएचके वर्ल्ड के नवीनतम शो ब्राउज़ करें",
        "th": "เรียกดูรายการล่าสุดของ NHK World",
        "my": "NHK World နောက်ဆုံးထွက်ရှိုးများကို ကြည့်ပါ။",
        "id": "Telusuri acara terbaru NHK World",
        "tr": "NHK World'ün en son programlarına göz atın",
        "uk": "Перегляньте останні шоу NHK World",
        "vi":"Duyệt các chương trình mới nhất của NHK World"
    },
    "NHK News": {
        "en": "NHK News",
        "ja": "NHKニュース",
        "zh": "NHK新闻",
        "zt": "NHK新聞",
        "ko": "NHK 뉴스",
        "es": "Noticias NHK",
        "fr": "NHK News",
        "pt": "Notícias da NHK",
        "ru": "Новости NHK",
        "ar": "أخبار NHK",
        "hi": "एनएचके न्यूज़",
        "th": "ข่าว NHK",
        "my": "NHK သတင်း",
        "id": "Berita NHK",
        "tr": "NHK Haberleri",
        "uk": "Новини NHK",
        "vi":"Tin tức NHK"
    },
    "All News Videos": {
        "en": "All News Videos",
        "ja": "すべてのニュース動画",
        "zh": "所有新闻视频",
        "zt": "所有新聞視頻",
        "ko": "모든 뉴스 영상",
        "es": "Todos los videos de noticias",
        "fr": "Toutes les vidéos d'actualité",
        "pt": "Todos os vídeos de notícias",
        "ru": "Все новостные видео",
        "ar": "جميع مقاطع الفيديو الإخبارية",
        "hi": "सभी समाचार वीडियो",
        "th": "วิดีโอข่าวทั้งหมด",
        "my": "သတင်းဗီဒီယိုအားလုံး",
        "id": "Semua Video Berita",
        "tr": "Tüm Haber Videoları",
        "uk": "Усі відео новини",
        "vi":"Tất cả video tin tức"
    },
    "Japan": {
        "en": "Japan",
        "ja": "日本",
        "zh": "日本",
        "zt": "日本",
        "ko": "일본",
        "es": "Japón",
        "fr": "Japon",
        "pt": "Japão",
        "ru": "Япония",
        "ar": "اليابان",
        "hi": "जापान",
        "th": "ญี่ปุ่น",
        "my": "ဂျပန်",
        "id": "Jepang",
        "tr": "Japonya",
        "uk": "Японія",
        "vi":"Nhật Bản"
    },
    "Asia": {
        "en": "Asia",
        "ja": "アジア",
        "zh": "亚洲",
        "zt": "亞洲",
        "ko": "아시아",
        "es": "Asia",
        "fr": "Asie",
        "pt": "Ásia",
        "ru": "Азия",
        "ar": "آسيا",
        "hi": "एशिया",
        "th": "เอเชีย",
        "my": "အာရှ",
        "id": "Asia",
        "tr": "Asya",
        "uk": "Азія",
        "vi":"Châu Á"
    },
    "World": {
        "en": "World",
        "ja": "世界",
        "zh": "世界",
        "zt": "世界",
        "ko": "세계",
        "es": "Mundo",
        "fr": "Monde",
        "pt": "Mundo",
        "ru": "Мир",
        "ar": "العالم",
        "hi": "विश्व",
        "th": "โลก",
        "my": "ကမ္ဘာ့",
        "id": "Dunia",
        "tr": "Dünya",
        "uk": "Світ",
        "vi":"Thế giới"
    },
    "Business & Tech": {
        "en": "Business & Tech",
        "ja": "ビジネス＆テクノロジー",
        "zh": "商业与科技",
        "zt": "商業與科技",
        "ko": "비즈니스 및 기술",
        "es": "Negocios y tecnología",
        "fr": "Économie et technologie",
        "pt": "Negócios e Tecnologia",
        "ru": "Бизнес и технологии",
        "ar": "الأعمال والتكنولوجيا",
        "hi": "व्यापार और तकनीक",
        "th": "ธุรกิจและเทคโนโลยี",
        "my": "စီးပွားရေးနှင့် နည်းပညာ",
        "id": "Bisnis & Teknologi",
        "tr": "İş ve Teknoloji",
        "uk": "Бізнес і технології",
        "vi":"Kinh doanh & Công nghệ"
    },
    "Special Clips": {
        "en": "Special Clips",
        "ja": "スペシャルクリップ",
        "zh": "特别片段",
        "zt": "特別片段",
        "ko": "특별 클립",
        "es": "Clips especiales",
        "fr": "Extraits spéciaux",
        "pt": "Clipes Especiais",
        "ru": "Специальные клипы",
        "ar": "مقاطع خاصة",
        "hi": "विशेष क्लिप",
        "th": "คลิปพิเศษ",
        "my": "အထူးဗီဒီယိုအပိုင်းများ",
        "id": "Klip Spesial",
        "tr": "Özel Klipler",
        "uk": "Спеціальні відео",
        "vi":"Đoạn phim đặc biệt"
    },

}

def _(key, lang):
    """Helper to get localized string with English fallback"""
    return UI_STRINGS.get(key, {}).get(lang, key)

def get_lang_code(addon):
    try:
        idx = int(addon.getSetting("language"))
        lang_name = LANG_OPTIONS[idx]
        return LANG_MAP.get(lang_name, "en")
    except Exception:
        return "en"

addon = xbmcaddon.Addon()
lang_code = get_lang_code(addon)

CATEGORIES = _("Categories", lang_code)
LATEST_VIDEOS = _("Latest Videos", lang_code)
LATEST_SHOWS = _("Latest Shows", lang_code)
TRENDING= _("Trending", lang_code)
CATEGORY_PLOT= _("Category Plot", lang_code)
VIDEO_PLOT = _("Video Plot", lang_code)
SHOW_PLOT = _("Show Plot", lang_code)
NHK_NEWS =_("NHK News", lang_code)
ALL_NEW_VIDEOS =_("All News Videos", lang_code)
JAPAN =_("Japan", lang_code)
ASIA =_("Asia", lang_code)
WORLD =_("World", lang_code)
BUSINESS_TECH =_("Business & Tech", lang_code)
SPECIAL_CLIPS =_("Special Clips", lang_code)
