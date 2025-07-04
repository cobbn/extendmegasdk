# ruff: noqa
from base64 import b64decode, b64encode
from hashlib import sha256
from http.cookiejar import MozillaCookieJar
from json import loads
from os import path as ospath
from os.path import join as path_join
from re import findall, match, search
from time import sleep
from urllib.parse import parse_qs, urlparse, quote, unquote
from uuid import uuid4

from cloudscraper import create_scraper
from lxml.etree import HTML
from requests import RequestException, Session, get, post
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from bot.core.config_manager import Config
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.ext_utils.help_messages import PASSWORD_ERROR_MESSAGE
from bot.helper.ext_utils.links_utils import is_share_link
from bot.helper.ext_utils.status_utils import speed_string_to_bytes

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"

debrid_link_supported_sites = [
    "1024tera.com",
    "1024terabox.com",
    "1dl.net",
    "1fichier.com",
    "24hd.club",
    "449unceremoniousnasoseptal.com",
    "4funbox.com",
    "4tube.com",
    "academicearth.org",
    "acast.com",
    "add-anime.net",
    "air.mozilla.org",
    "albavido.xyz",
    "alterupload.com",
    "alphaporno.com",
    "amazonaws.com",
    "anime789.com",
    "animalist.com",
    "animalplanet.com",
    "apkadmin.com",
    "aparat.com",
    "anysex.com",
    "audi-mediacenter.com",
    "audioboom.com",
    "audiomack.com",
    "bayfiles.com",
    "beeg.com",
    "camdemy.com",
    "chilloutzone.net",
    "cjoint.net",
    "cinema.arte.tv",
    "clickndownload.org",
    "clicknupload.cc",
    "clicknupload.club",
    "clicknupload.co",
    "clicknupload.download",
    "clicknupload.link",
    "clicknupload.org",
    "clubic.com",
    "clyp.it",
    "concert.arte.tv",
    "creative.arte.tv",
    "daclips.in",
    "dailyplanet.pw",
    "dailymail.co.uk",
    "dailymotion.com",
    "ddc.arte.tv",
    "ddownload.com",
    "ddl.to",
    "democracynow.org",
    "depositfiles.com",
    "desfichiers.com",
    "destinationamerica.com",
    "dfichiers.com",
    "diasfem.com",
    "dl4free.com",
    "dl.free.fr",
    "dood.cx",
    "dood.la",
    "dood.pm",
    "dood.re",
    "dood.sh",
    "dood.so",
    "dood.stream",
    "dood.video",
    "dood.watch",
    "dood.ws",
    "dood.yt",
    "dooood.com",
    "doods.pro",
    "doods.yt",
    "drop.download",
    "dropapk.to",
    "dropbox.com",
    "ds2play.com",
    "ds2video.com",
    "dutrag.com",
    "e.pcloud.link",
    "ebaumsworld.com",
    "easybytez.com",
    "easybytez.eu",
    "easybytez.me",
    "easyupload.io",
    "eitb.tv",
    "elfile.net",
    "elitefile.net",
    "emload.com",
    "embedwish.com",
    "embedsito.com",
    "fcdn.stream",
    "fastfile.cc",
    "feurl.com",
    "femax20.com",
    "fembed-hd.com",
    "fembed.com",
    "fembed9hd.com",
    "femoload.xyz",
    "file.al",
    "fileaxa.com",
    "filecat.net",
    "filedot.to",
    "filedot.xyz",
    "filefactory.com",
    "filelions.co",
    "filelions.live",
    "filelions.online",
    "filelions.site",
    "filelions.to",
    "filenext.com",
    "filer.net",
    "filerice.com",
    "filesfly.cc",
    "filespace.com",
    "filestore.me",
    "filextras.com",
    "fikper.com",
    "flashbit.cc",
    "flipagram.com",
    "footyroom.com",
    "formula1.com",
    "franceculture.fr",
    "free.fr",
    "freeterabox.com",
    "future.arte.tv",
    "gameinformer.com",
    "gamersyde.com",
    "gcloud.live",
    "gigapeta.com",
    "gibibox.com",
    "github.com",
    "gofile.io",
    "goloady.com",
    "goaibox.com",
    "gorillavid.in",
    "hellporno.com",
    "hentai.animestigma.com",
    "highload.to",
    "hitf.cc",
    "hitfile.net",
    "hornbunny.com",
    "hotfile.io",
    "html5-player.libsyn.com",
    "hulkshare.com",
    "hxfile.co",
    "icerbox.com",
    "imdb.com",
    "info.arte.tv",
    "instagram.com",
    "investigationdiscovery.com",
    "isra.cloud",
    "itar-tass.com",
    "jamendo.com",
    "jove.com",
    "jplayer.net",
    "jumploads.com",
    "k.to",
    "k2s.cc",
    "katfile.com",
    "keep2share.cc",
    "keep2share.com",
    "keek.com",
    "keezmovies.com",
    "khanacademy.org",
    "kickstarter.com",
    "kissmovies.net",
    "kitabmarkaz.xyz",
    "krasview.ru",
    "krakenfiles.com",
    "kshared.com",
    "la7.it",
    "lbx.to",
    "lci.fr",
    "libsyn.com",
    "linkbox.to",
    "load.to",
    "liveleak.com",
    "livestream.com",
    "lulacloud.com",
    "m6.fr",
    "mediafile.cc",
    "mediafire.com",
    "mediafirefolder.com",
    "mediashore.org",
    "megadl.fr",
    "megadl.org",
    "mega.co.nz",
    "mega.nz",
    "mesfichiers.fr",
    "mesfichiers.org",
    "metacritic.com",
    "mexa.sh",
    "mexashare.com",
    "mgoon.com",
    "mirrobox.com",
    "mixcloud.com",
    "mixdrop.club",
    "mixdrop.co",
    "mixdrop.sx",
    "mixdrop.to",
    "modsbase.com",
    "momerybox.com",
    "mojvideo.com",
    "moviemaniac.org",
    "movpod.in",
    "mrdhan.com",
    "mx-sh.net",
    "mycloudz.cc",
    "musicplayon.com",
    "myspass.de",
    "myfile.is",
    "nephobox.com",
    "nelion.me",
    "new.livestream.com",
    "news.yahoo.com",
    "nitro.download",
    "nitroflare.com",
    "noregx.debrid.link",
    "odatv.com",
    "onionstudios.com",
    "opvid.online",
    "opvid.org",
    "ora.tv",
    "osdn.net",
    "pcloud.com",
    "piecejointe.net",
    "pixeldrain.com",
    "play.fm",
    "play.lcp.fr",
    "player.vimeo.com",
    "player.vimeopro.com",
    "plays.tv",
    "playvid.com",
    "pjointe.com",
    "pornhd.com",
    "pornhub.com",
    "prefiles.com",
    "pyvideo.org",
    "racaty.com",
    "rapidgator.asia",
    "rapidgator.net",
    "reputationsheriffkennethsand.com",
    "reverbnation.com",
    "revision3.com",
    "rg.to",
    "rts.ch",
    "rtve.es",
    "salefiles.com",
    "sbs.com.au",
    "sciencechannel.com",
    "screen.yahoo.com",
    "scribd.com",
    "seeker.com",
    "send.cm",
    "sendspace.com",
    "sexhd.co",
    "shrdsk.me",
    "sharemods.com",
    "sharinglink.club",
    "sites.arte.tv",
    "skysports.com",
    "slmaxed.com",
    "sltube.org",
    "slwatch.co",
    "solidfiles.com",
    "soundcloud.com",
    "soundgasm.net",
    "steamcommunity.com",
    "steampowered.com",
    "store.steampowered.com",
    "stream.cz",
    "streamable.com",
    "streamcloud.eu",
    "streamhub.ink",
    "streamhub.to",
    "streamlare.com",
    "streamtape.cc",
    "streamtape.co",
    "streamtape.com",
    "streamtape.net",
    "streamtape.to",
    "streamtape.wf",
    "streamtape.xyz",
    "streamta.pe",
    "streamvid.net",
    "streamwish.to",
    "subyshare.com",
    "sunporno.com",
    "superplayxyz.club",
    "supervideo.tv",
    "swisstransfer.com",
    "suzihaza.com",
    "teachertube.com",
    "teamcoco.com",
    "ted.com",
    "tenvoi.com",
    "terabox.app",
    "terabox.com",
    "terabox.link",
    "teraboxapp.com",
    "teraboxlink.com",
    "teraboxshare.com",
    "terafileshare.com",
    "terasharelink.com",
    "terazilla.com",
    "tezfiles.com",
    "thescene.com",
    "thesixtyone.com",
    "there.to",
    "tfo.org",
    "tlc.com",
    "tmpsend.com",
    "tnaflix.com",
    "transfert.free.fr",
    "trubobit.com",
    "turb.cc",
    "turbabit.com",
    "turbobit.cc",
    "turbobit.live",
    "turbobit.net",
    "turbobit.online",
    "turbobit.pw",
    "turbobit.ru",
    "turbobitlt.co",
    "turboget.net",
    "turbo.fr",
    "turbo.to",
    "turb.pw",
    "turb.to",
    "tu.tv",
    "uloz.to",
    "ulozto.cz",
    "ulozto.net",
    "ulozto.sk",
    "up-4ever.com",
    "up-4ever.net",
    "upload-4ever.com",
    "uptobox.com",
    "uptobox.eu",
    "uptobox.fr",
    "uptobox.link",
    "uptostream.com",
    "uptostream.eu",
    "uptostream.fr",
    "uptostream.link",
    "upvid.biz",
    "upvid.cloud",
    "upvid.co",
    "upvid.host",
    "upvid.live",
    "upvid.pro",
    "uqload.co",
    "uqload.com",
    "uqload.io",
    "userload.co",
    "usersdrive.com",
    "vanfem.com",
    "vbox7.com",
    "vcdn.io",
    "vcdnplay.com",
    "veehd.com",
    "veoh.com",
    "vid.me",
    "vidohd.com",
    "vidoza.net",
    "vidsource.me",
    "vimeopro.com",
    "viplayer.cc",
    "voe-un-block.com",
    "voe-unblock.com",
    "voe.sx",
    "voeun-block.net",
    "voeunbl0ck.com",
    "voeunblck.com",
    "voeunblk.com",
    "voeunblock1.com",
    "voeunblock2.com",
    "voeunblock3.com",
    "votrefile.xyz",
    "votrefiles.club",
    "wat.tv",
    "wdupload.com",
    "wimp.com",
    "world-files.com",
    "worldbytez.com",
    "wupfile.com",
    "xstreamcdn.com",
    "yahoo.com",
    "yodbox.com",
    "youdbox.com",
    "youtube.com",
    "youtu.be",
    "zachowajto.pl",
    "zidiplay.com",
]


def direct_link_generator(link):
    """direct links generator"""
    domain = urlparse(link).hostname
    if not domain:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
    if "yadi.sk" in link or "disk.yandex." in link:
        return yandex_disk(link)
    if Config.DEBRID_LINK_API and any(
        x in domain for x in debrid_link_supported_sites
    ):
        return debrid_link(link)
    if "buzzheavier.com" in domain:
        return buzzheavier(link)
    if "devuploads" in domain:
        return devuploads(link)
    if "lulacloud.com" in domain:
        return lulacloud(link)
    if "uploadhaven" in domain:
        return uploadhaven(link)
    if "fuckingfast.co" in domain:
        return fuckingfast_dl(link)
    if "osdn.net" in domain:
        return osdn(link)
    if "github.com" in domain:
        return github(link)
    if "hxfile.co" in domain:
        return hxfile(link)
    if "1drv.ms" in domain:
        return onedrive(link)
    if any(x in domain for x in ["pixeldrain.com", "pixeldra.in"]):
        return pixeldrain(link)
    if "racaty" in domain:
        return racaty(link)
    if "1fichier.com" in domain:
        return fichier(link)
    if "solidfiles.com" in domain:
        return solidfiles(link)
    if "krakenfiles.com" in domain:
        return krakenfiles(link)
    if "upload.ee" in domain:
        return uploadee(link)
    if "gofile.io" in domain:
        return gofile(link)
    if "send.cm" in domain:
        return send_cm(link)
    if "tmpsend.com" in domain:
        return tmpsend(link)
    if "easyupload.io" in domain:
        return easyupload(link)
    if "streamvid.net" in domain:
        return streamvid(link)
    if "shrdsk.me" in domain:
        return shrdsk(link)
    if "u.pcloud.link" in domain:
        return pcloud(link)
    if "qiwi.gg" in domain:
        return qiwi(link)
    if "mp4upload.com" in domain:
        return mp4upload(link)
    if "berkasdrive.com" in domain:
        return berkasdrive(link)
    if "swisstransfer.com" in domain:
        return swisstransfer(link)
    if "instagram.com" in domain:
        return instagram(link)
    if any(x in domain for x in ["akmfiles.com", "akmfls.xyz"]):
        return akmfiles(link)
    if any(
        x in domain
        for x in [
            "dood.watch",
            "doodstream.com",
            "dood.to",
            "dood.so",
            "dood.cx",
            "dood.la",
            "dood.ws",
            "dood.sh",
            "doodstream.co",
            "dood.pm",
            "dood.wf",
            "dood.re",
            "dood.video",
            "dooood.com",
            "dood.yt",
            "doods.yt",
            "dood.stream",
            "doods.pro",
            "ds2play.com",
            "d0o0d.com",
            "ds2video.com",
            "do0od.com",
            "d000d.com",
        ]
    ):
        return doods(link)
    if any(
        x in domain
        for x in [
            "streamtape.com",
            "streamtape.co",
            "streamtape.cc",
            "streamtape.to",
            "streamtape.net",
            "streamta.pe",
            "streamtape.xyz",
        ]
    ):
        return streamtape(link)
    if any(x in domain for x in ["wetransfer.com", "we.tl"]):
        return wetransfer(link)
    if any(
        x in domain
        for x in [
            "terabox.com",
            "nephobox.com",
            "4funbox.com",
            "mirrobox.com",
            "momerybox.com",
            "teraboxapp.com",
            "1024tera.com",
            "terabox.app",
            "gibibox.com",
            "goaibox.com",
            "terasharelink.com",
            "teraboxlink.com",
            "freeterabox.com",
            "1024terabox.com",
            "teraboxshare.com",
            "terafileshare.com",
            "terabox.club",
        ]
    ):
        return terabox(link)
    if any(
        x in domain
        for x in [
            "filelions.co",
            "filelions.site",
            "filelions.live",
            "filelions.to",
            "mycloudz.cc",
            "cabecabean.lol",
            "filelions.online",
            "embedwish.com",
            "kitabmarkaz.xyz",
            "wishfast.top",
            "streamwish.to",
            "kissmovies.net",
        ]
    ):
        return filelions_and_streamwish(link)
    if any(x in domain for x in ["streamhub.ink", "streamhub.to"]):
        return streamhub(link)
    if any(
        x in domain
        for x in [
            "linkbox.to",
            "lbx.to",
            "teltobx.net",
            "telbx.net",
        ]
    ):
        return linkBox(link)
    if is_share_link(link):
        if "gdtot" in domain:
            return gdtot(link)
        if "filepress" in domain:
            return filepress(link)
        return sharer_scraper(link)
    if any(
        x in domain
        for x in [
            "anonfiles.com",
            "zippyshare.com",
            "letsupload.io",
            "hotfile.io",
            "bayfiles.com",
            "megaupload.nz",
            "letsupload.cc",
            "filechan.org",
            "myfile.is",
            "vshare.is",
            "rapidshare.nu",
            "lolabits.se",
            "openload.cc",
            "share-online.is",
            "upvid.cc",
            "uptobox.com",
            "uptobox.fr",
        ]
    ):
        raise DirectDownloadLinkException(f"ERROR: R.I.P {domain}")
    raise DirectDownloadLinkException(f"No Direct link function found for {link}")


def get_captcha_token(session, params):
    recaptcha_api = "https://www.google.com/recaptcha/api2"
    res = session.get(f"{recaptcha_api}/anchor", params=params)
    anchor_html = HTML(res.text)
    if not (
        anchor_token := anchor_html.xpath('//input[@id="recaptcha-token"]/@value')
    ):
        return None
    params["c"] = anchor_token[0]
    params["reason"] = "q"
    res = session.post(f"{recaptcha_api}/reload", params=params)
    if token := findall(r'"rresp","(.*?)"', res.text):
        return token[0]
    return None


def debrid_link(url):
    cget = create_scraper().request
    resp = cget(
        "POST",
        f"https://debrid-link.com/api/v2/downloader/add?access_token={Config.DEBRID_LINK_API}",
        data={"url": url},
    ).json()
    if resp["success"] != True:
        raise DirectDownloadLinkException(
            f"ERROR: {resp['error']} & ERROR ID: {resp['error_id']}"
        )
    if isinstance(resp["value"], dict):
        return resp["value"]["downloadUrl"]
    elif isinstance(resp["value"], list):
        details = {
            "contents": [],
            "title": unquote(url.rstrip("/").split("/")[-1]),
            "total_size": 0,
        }
        for dl in resp["value"]:
            if dl.get("expired", False):
                continue
            item = {
                "path": details["title"],
                "filename": dl["name"],
                "url": dl["downloadUrl"],
            }
            if "size" in dl:
                details["total_size"] += dl["size"]
            details["contents"].append(item)
        return details


def buzzheavier(url):
    """
    Generate a direct download link for buzzheavier URLs.
    @param link: URL from buzzheavier
    @return: Direct download link
    """
    pattern = r"^https?://buzzheavier\.com/[a-zA-Z0-9]+$"
    if not match(pattern, url):
        return url

    def _bhscraper(url, folder=False):
        session = Session()
        if "/download" not in url:
            url += "/download"
        url = url.strip()
        session.headers.update(
            {
                "referer": url.split("/download")[0],
                "hx-current-url": url.split("/download")[0],
                "hx-request": "true",
                "priority": "u=1, i",
            }
        )
        try:
            response = session.get(url)
            d_url = response.headers.get("Hx-Redirect")
            if not d_url:
                if not folder:
                    raise DirectDownloadLinkException(
                        f"ERROR: Gagal mendapatkan data"
                    )
                return
            return d_url
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e

    with Session() as session:
        tree = HTML(session.get(url).text)
        if link := tree.xpath(
            "//a[contains(@class, 'link-button') and contains(@class, 'gay-button')]/@hx-get"
        ):
            return _bhscraper("https://buzzheavier.com" + link[0])
        elif folders := tree.xpath("//tbody[@id='tbody']/tr"):
            details = {"contents": [], "title": "", "total_size": 0}
            for data in folders:
                try:
                    filename = data.xpath(".//a")[0].text.strip()
                    _id = data.xpath(".//a")[0].attrib.get("href", "").strip()
                    size = data.xpath(".//td[@class='text-center']/text()")[
                        0
                    ].strip()
                    url = _bhscraper(f"https://buzzheavier.com{_id}", True)
                    item = {
                        "path": "",
                        "filename": filename,
                        "url": url,
                    }
                    details["contents"].append(item)
                    size = speed_string_to_bytes(size)
                    details["total_size"] += size
                except:
                    continue
            details["title"] = tree.xpath("//span/text()")[0].strip()
            return details
        else:
            raise DirectDownloadLinkException("ERROR: No download link found")


def fuckingfast_dl(url):
    """
    Generate a direct download link for fuckingfast.co URLs.
    @param url: URL from fuckingfast.co
    @return: Direct download link
    """
    url = url.strip()

    try:
        response = get(url)
        content = response.text
        pattern = r'window\.open\((["\'])(https://fuckingfast\.co/dl/[^"\']+)\1'
        match = search(pattern, content)

        if not match:
            raise DirectDownloadLinkException(
                "ERROR: Could not find download link in page"
            )

        direct_url = match.group(2)
        return direct_url

    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e


def lulacloud(url):
    """
    Generate a direct download link for www.lulacloud.com URLs.
    @param url: URL from www.lulacloud.com
    @return: Direct download link
    """
    try:
        res = post(url, headers={"Referer": url}, allow_redirects=False)
        return res.headers["location"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e


def devuploads(url):
    """
    Generate a direct download link for devuploads.com URLs.
    @param url: URL from devuploads.com
    @return: Direct download link
    """
    with Session() as session:
        res = session.get(url)
        html = HTML(res.text)
        if not html.xpath("//input[@name]"):
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        data = {i.get("name"): i.get("value") for i in html.xpath("//input[@name]")}
        res = session.post("https://gujjukhabar.in/", data=data)
        html = HTML(res.text)
        if not html.xpath("//input[@name]"):
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        data = {i.get("name"): i.get("value") for i in html.xpath("//input[@name]")}
        resp = session.get(
            "https://du2.devuploads.com/dlhash.php",
            headers={
                "Origin": "https://gujjukhabar.in",
                "Referer": "https://gujjukhabar.in/",
            },
        )
        if not resp.text:
            raise DirectDownloadLinkException("ERROR: Unable to find ipp value")
        data["ipp"] = resp.text.strip()
        if not data.get("rand"):
            raise DirectDownloadLinkException("ERROR: Unable to find rand value")
        randpost = session.post(
            "https://devuploads.com/token/token.php",
            data={"rand": data["rand"], "msg": ""},
            headers={
                "Origin": "https://gujjukhabar.in",
                "Referer": "https://gujjukhabar.in/",
            },
        )
        if not randpost:
            raise DirectDownloadLinkException("ERROR: Unable to find xd value")
        data["xd"] = randpost.text.strip()
        res = session.post(url, data=data)
        html = HTML(res.text)
        if not html.xpath("//input[@name='orilink']/@value"):
            raise DirectDownloadLinkException("ERROR: Unable to find Direct Link")
        direct_link = html.xpath("//input[@name='orilink']/@value")
        return direct_link[0]


def uploadhaven(url):
    """
    Generate a direct download link for uploadhaven.com URLs.
    @param url: URL from uploadhaven.com
    @return: Direct download link
    """
    try:
        res = get(url, headers={"Referer": "http://steamunlocked.net/"})
        html = HTML(res.text)
        if not html.xpath('//form[@method="POST"]//input'):
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        data = {
            i.get("name"): i.get("value")
            for i in html.xpath('//form[@method="POST"]//input')
        }
        sleep(15)
        res = post(url, data=data, headers={"Referer": url}, cookies=res.cookies)
        html = HTML(res.text)
        if not html.xpath('//div[@class="alert alert-success mb-0"]//a'):
            raise DirectDownloadLinkException("ERROR: Unable to find link data")
        a = html.xpath('//div[@class="alert alert-success mb-0"]//a')[0]
        return a.get("href")
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {str(e)}") from e


def osdn(url):
    with create_scraper() as session:
        try:
            html = HTML(session.get(url).text)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        if not (direct_link := html.xapth('//a[@class="mirror_link"]/@href')):
            raise DirectDownloadLinkException("ERROR: Direct link not found")
        return f"https://osdn.net{direct_link[0]}"


def yandex_disk(url: str) -> str:
    """Yandex.Disk direct link generator
    Based on https://github.com/wldhx/yadisk-direct"""
    try:
        link = findall(r"\b(https?://(yadi\.sk|disk\.yandex\.(com|ru))\S+)", url)[0][
            0
        ]
    except IndexError:
        return "No Yandex.Disk links found\n"
    api = "https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}"
    try:
        return get(api.format(link)).json()["href"]
    except KeyError as e:
        raise DirectDownloadLinkException(
            "ERROR: File not found/Download limit reached",
        ) from e


def github(url):
    """GitHub direct links generator"""
    try:
        findall(r"\bhttps?://.*github\.com.*releases\S+", url)[0]
    except IndexError as e:
        raise DirectDownloadLinkException("No GitHub Releases links found") from e
    with create_scraper() as session:
        _res = session.get(url, stream=True, allow_redirects=False)
        if "location" in _res.headers:
            return _res.headers["location"]
        raise DirectDownloadLinkException("ERROR: Can't extract the link")


def hxfile(url):
    if not ospath.isfile("hxfile.txt"):
        raise DirectDownloadLinkException("ERROR: hxfile.txt (cookies) Not Found!")
    try:
        jar = MozillaCookieJar()
        jar.load("hxfile.txt")
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    cookies = {cookie.name: cookie.value for cookie in jar}
    try:
        if url.strip().endswith(".html"):
            url = url[:-5]
        file_code = url.split("/")[-1]
        html = HTML(
            post(
                url,
                data={"op": "download2", "id": file_code},
                cookies=cookies,
            ).text
        )
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if direct_link := html.xpath("//a[@class='btn btn-dow']/@href"):
        header = [f"Referer: {url}"]
        return direct_link[0], header
    raise DirectDownloadLinkException("ERROR: Direct download link not found")


def onedrive(link):
    """Onedrive direct link generator
    By https://github.com/junedkh"""
    with create_scraper() as session:
        try:
            link = session.get(link).url
            parsed_link = urlparse(link)
            link_data = parse_qs(parsed_link.query)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        if not link_data:
            raise DirectDownloadLinkException("ERROR: Unable to find link_data")
        folder_id = link_data.get("resid")
        if not folder_id:
            raise DirectDownloadLinkException("ERROR: folder id not found")
        folder_id = folder_id[0]
        authkey = link_data.get("authkey")
        if not authkey:
            raise DirectDownloadLinkException("ERROR: authkey not found")
        authkey = authkey[0]
        boundary = uuid4()
        headers = {"content-type": f"multipart/form-data;boundary={boundary}"}
        data = f"--{boundary}\r\nContent-Disposition: form-data;name=data\r\nPrefer: Migration=EnableRedirect;FailOnMigratedFiles\r\nX-HTTP-Method-Override: GET\r\nContent-Type: application/json\r\n\r\n--{boundary}--"
        try:
            resp = session.get(
                f"https://api.onedrive.com/v1.0/drives/{folder_id.split('!', 1)[0]}/items/{folder_id}?$select=id,@content.downloadUrl&ump=1&authKey={authkey}",
                headers=headers,
                data=data,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    if "@content.downloadUrl" not in resp:
        raise DirectDownloadLinkException("ERROR: Direct link not found")
    return resp["@content.downloadUrl"]


def pixeldrain(url):
    try:
        url = url.rstrip("/")
        code = url.split("/")[-1].split("?", 1)[0]
        response = get("https://pd.cybar.xyz/", allow_redirects=True)
        return response.url + code
    except Exception as e:
        raise DirectDownloadLinkException("ERROR: Direct link not found")


def streamtape(url):
    splitted_url = url.split("/")
    _id = splitted_url[4] if len(splitted_url) >= 6 else splitted_url[-1]
    try:
        html = HTML(get(url).text)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    script = html.xpath(
        "//script[contains(text(),'ideoooolink')]/text()",
    ) or html.xpath("//script[contains(text(),'ideoolink')]/text()")
    if not script:
        raise DirectDownloadLinkException("ERROR: requeries script not found")
    if not (link := findall(r"(&expires\S+)'", script[0])):
        raise DirectDownloadLinkException("ERROR: Download link not found")
    return f"https://streamtape.com/get_video?id={_id}{link[-1]}"


def racaty(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            json_data = {"op": "download2", "id": url.split("/")[-1]}
            html = HTML(session.post(url, data=json_data).text)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    if direct_link := html.xpath("//a[@id='uniqueExpirylink']/@href"):
        return direct_link[0]
    raise DirectDownloadLinkException("ERROR: Direct link not found")


def fichier(link):
    """1Fichier direct link generator
    Based on https://github.com/Maujar
    """
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    gan = match(regex, link)
    if not gan:
        raise DirectDownloadLinkException("ERROR: The link you entered is wrong!")
    if "::" in link:
        pswd = link.split("::")[-1]
        url = link.split("::")[-2]
    else:
        pswd = None
        url = link
    cget = create_scraper().request
    try:
        if pswd is None:
            req = cget("post", url)
        else:
            pw = {"pass": pswd}
            req = cget("post", url, data=pw)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if req.status_code == 404:
        raise DirectDownloadLinkException(
            "ERROR: File not found/The link you entered is wrong!",
        )
    html = HTML(req.text)
    if dl_url := html.xpath('//a[@class="ok btn-general btn-orange"]/@href'):
        return dl_url[0]
    if not (ct_warn := html.xpath('//div[@class="ct_warn"]')):
        raise DirectDownloadLinkException(
            "ERROR: Error trying to generate Direct Link from 1fichier!",
        )
    if len(ct_warn) == 3:
        str_2 = ct_warn[-1].text
        if "you must wait" in str_2.lower():
            if numbers := [int(word) for word in str_2.split() if word.isdigit()]:
                raise DirectDownloadLinkException(
                    f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute.",
                )
            raise DirectDownloadLinkException(
                "ERROR: 1fichier is on a limit. Please wait a few minutes/hour.",
            )
        if "protect access" in str_2.lower():
            raise DirectDownloadLinkException(
                f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(link)}",
            )
        raise DirectDownloadLinkException(
            "ERROR: Failed to generate Direct Link from 1fichier!",
        )
    if len(ct_warn) == 4:
        str_1 = ct_warn[-2].text
        str_3 = ct_warn[-1].text
        if "you must wait" in str_1.lower():
            if numbers := [int(word) for word in str_1.split() if word.isdigit()]:
                raise DirectDownloadLinkException(
                    f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute.",
                )
            raise DirectDownloadLinkException(
                "ERROR: 1fichier is on a limit. Please wait a few minutes/hour.",
            )
        if "bad password" in str_3.lower():
            raise DirectDownloadLinkException(
                "ERROR: The password you entered is wrong!",
            )
    raise DirectDownloadLinkException(
        "ERROR: Error trying to generate Direct Link from 1fichier!",
    )


def solidfiles(url):
    """Solidfiles direct link generator
    Based on https://github.com/Xonshiz/SolidFiles-Downloader
    By https://github.com/Jusidama18"""
    with create_scraper() as session:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
            }
            pageSource = session.get(url, headers=headers).text
            mainOptions = str(
                search(r"viewerOptions\'\,\ (.*?)\)\;", pageSource).group(1),
            )
            return loads(mainOptions)["downloadUrl"]
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e


def krakenfiles(url):
    with Session() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        html = HTML(_res.text)
        if post_url := html.xpath('//form[@id="dl-form"]/@action'):
            post_url = f"https://krakenfiles.com{post_url[0]}"
        else:
            raise DirectDownloadLinkException("ERROR: Unable to find post link.")
        if token := html.xpath('//input[@id="dl-token"]/@value'):
            data = {"token": token[0]}
        else:
            raise DirectDownloadLinkException(
                "ERROR: Unable to find token for post.",
            )
        try:
            _json = session.post(post_url, data=data).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__} While send post request",
            ) from e
    if _json["status"] != "ok":
        raise DirectDownloadLinkException(
            "ERROR: Unable to find download after post request",
        )
    return _json["url"]


def uploadee(url):
    with create_scraper() as session:
        try:
            html = HTML(session.get(url).text)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    if link := html.xpath("//a[@id='d_l']/@href"):
        return link[0]
    raise DirectDownloadLinkException("ERROR: Direct Link not found")


def terabox(url):
    from bot.core.config_manager import Config

    if "/file/" in url:
        return url

    # Use TERABOX_PROXY if configured, otherwise use default API
    if hasattr(Config, "TERABOX_PROXY") and Config.TERABOX_PROXY:
        proxy_url = Config.TERABOX_PROXY.rstrip("/")
        api_url = f"{proxy_url}/api?url={quote(url)}"
    else:
        api_url = f"https://wdzone-terabox-api.vercel.app/api?url={quote(url)}"

    try:
        with Session() as session:
            req = session.get(api_url, headers={"User-Agent": user_agent}).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e

    details = {"contents": [], "title": "", "total_size": 0}
    if "✅ Status" in req:
        for data in req["📜 Extracted Info"]:
            item = {
                "path": "",
                "filename": data["📂 Title"],
                "url": data["🔽 Direct Download Link"],
            }
            details["contents"].append(item)
            size = (data["📏 Size"]).replace(" ", "")
            size = speed_string_to_bytes(size)
            details["total_size"] += size
        details["title"] = req["📜 Extracted Info"][0]["📂 Title"]
        if len(details["contents"]) == 1:
            return details["contents"][0]["url"]
        return details
    else:
        raise DirectDownloadLinkException("ERROR: File not found!")


def filepress(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            raw = urlparse(url)
            json_data = {
                "id": raw.path.split("/")[-1],
                "method": "publicDownlaod",
            }
            api = f"{raw.scheme}://{raw.hostname}/api/file/downlaod/"
            res2 = session.post(
                api,
                headers={"Referer": f"{raw.scheme}://{raw.hostname}"},
                json=json_data,
            ).json()
            json_data2 = {
                "id": res2["data"],
                "method": "publicUserDownlaod",
            }
            api2 = "https://new2.filepress.store/api/file/downlaod2/"
            res = session.post(
                api2,
                headers={"Referer": f"{raw.scheme}://{raw.hostname}"},
                json=json_data2,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    if "data" not in res:
        raise DirectDownloadLinkException(f"ERROR: {res['statusText']}")
    return f"https://drive.google.com/uc?id={res['data']}&export=download"


def gdtot(url):
    cget = create_scraper().request
    try:
        res = cget("GET", f"https://gdtot.pro/file/{url.split('/')[-1]}")
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    token_url = HTML(res.text).xpath(
        "//a[contains(@class,'inline-flex items-center justify-center')]/@href",
    )
    if not token_url:
        try:
            url = cget("GET", url).url
            p_url = urlparse(url)
            res = cget(
                "GET",
                f"{p_url.scheme}://{p_url.hostname}/ddl/{url.split('/')[-1]}",
            )
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        if (
            drive_link := findall(r"myDl\('(.*?)'\)", res.text)
        ) and "drive.google.com" in drive_link[0]:
            return drive_link[0]
        raise DirectDownloadLinkException(
            "ERROR: Drive Link not found, Try in your broswer",
        )
    token_url = token_url[0]
    try:
        token_page = cget("GET", token_url)
    except Exception as e:
        raise DirectDownloadLinkException(
            f"ERROR: {e.__class__.__name__} with {token_url}",
        ) from e
    path = findall(r'\("(.*?)"\)', token_page.text)
    if not path:
        raise DirectDownloadLinkException("ERROR: Cannot bypass this")
    path = path[0]
    raw = urlparse(token_url)
    final_url = f"{raw.scheme}://{raw.hostname}{path}"
    return sharer_scraper(final_url)


def sharer_scraper(url):
    cget = create_scraper().request
    try:
        url = cget("GET", url).url
        raw = urlparse(url)
        header = {
            "useragent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.548.0 Safari/534.10",
        }
        res = cget("GET", url, headers=header)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    key = findall(r'"key",\s+"(.*?)"', res.text)
    if not key:
        raise DirectDownloadLinkException("ERROR: Key not found!")
    key = key[0]
    if not HTML(res.text).xpath("//button[@id='drc']"):
        raise DirectDownloadLinkException(
            "ERROR: This link don't have direct download button",
        )
    boundary = uuid4()
    headers = {
        "Content-Type": f"multipart/form-data; boundary=----WebKitFormBoundary{boundary}",
        "x-token": raw.hostname,
        "useragent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/7.0.548.0 Safari/534.10",
    }

    data = (
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action"\r\n\r\ndirect\r\n'
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key}\r\n'
        f'------WebKitFormBoundary{boundary}\r\nContent-Disposition: form-data; name="action_token"\r\n\r\n\r\n'
        f"------WebKitFormBoundary{boundary}--\r\n"
    )
    try:
        res = cget(
            "POST",
            url,
            cookies=res.cookies,
            headers=headers,
            data=data,
        ).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if "url" not in res:
        raise DirectDownloadLinkException(
            "ERROR: Drive Link not found, Try in your broswer",
        )
    if (
        "drive.google.com" in res["url"]
        or "drive.usercontent.google.com" in res["url"]
    ):
        return res["url"]
    try:
        res = cget("GET", res["url"])
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if (
        drive_link := HTML(res.text).xpath("//a[contains(@class,'btn')]/@href")
    ) and (
        "drive.google.com" in drive_link[0]
        or "drive.usercontent.google.com" in drive_link[0]
    ):
        return drive_link[0]
    raise DirectDownloadLinkException(
        "ERROR: Drive Link not found, Try in your broswer",
    )


def wetransfer(url):
    with create_scraper() as session:
        try:
            url = session.get(url).url
            splited_url = url.split("/")
            json_data = {
                "security_hash": splited_url[-1],
                "intent": "entire_transfer",
            }
            res = session.post(
                f"https://wetransfer.com/api/v4/transfers/{splited_url[-2]}/download",
                json=json_data,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    if "direct_link" in res:
        return res["direct_link"]
    if "message" in res:
        raise DirectDownloadLinkException(f"ERROR: {res['message']}")
    if "error" in res:
        raise DirectDownloadLinkException(f"ERROR: {res['error']}")
    raise DirectDownloadLinkException("ERROR: cannot find direct link")


def akmfiles(url):
    with create_scraper() as session:
        try:
            html = HTML(
                session.post(
                    url,
                    data={"op": "download2", "id": url.split("/")[-1]},
                ).text,
            )
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    if direct_link := html.xpath("//a[contains(@class,'btn btn-dow')]/@href"):
        return direct_link[0]
    raise DirectDownloadLinkException("ERROR: Direct link not found")


def shrdsk(url):
    with create_scraper() as session:
        try:
            _json = session.get(
                f"https://us-central1-affiliate2apk.cloudfunctions.net/get_data?shortid={url.split('/')[-1]}",
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        if "download_data" not in _json:
            raise DirectDownloadLinkException("ERROR: Download data not found")
        try:
            _res = session.get(
                f"https://shrdsk.me/download/{_json['download_data']}",
                allow_redirects=False,
            )
            if "Location" in _res.headers:
                return _res.headers["Location"]
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    raise DirectDownloadLinkException("ERROR: cannot find direct link in headers")


def linkBox(url: str):
    parsed_url = urlparse(url)
    try:
        shareToken = parsed_url.path.split("/")[-1]
    except Exception:
        raise DirectDownloadLinkException("ERROR: invalid URL")

    details = {"contents": [], "title": "", "total_size": 0}

    def __singleItem(session, itemId):
        try:
            _json = session.get(
                "https://www.linkbox.to/api/file/detail",
                params={"itemId": itemId},
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        data = _json["data"]
        if not data:
            if "msg" in _json:
                raise DirectDownloadLinkException(f"ERROR: {_json['msg']}")
            raise DirectDownloadLinkException("ERROR: data not found")
        itemInfo = data["itemInfo"]
        if not itemInfo:
            raise DirectDownloadLinkException("ERROR: itemInfo not found")
        filename = itemInfo["name"]
        sub_type = itemInfo.get("sub_type")
        if sub_type and not filename.endswith(sub_type):
            filename += f".{sub_type}"
        if not details["title"]:
            details["title"] = filename
        item = {
            "path": "",
            "filename": filename,
            "url": itemInfo["url"],
        }
        if "size" in itemInfo:
            size = itemInfo["size"]
            if isinstance(size, str) and size.isdigit():
                size = float(size)
            details["total_size"] += size
        details["contents"].append(item)

    def __fetch_links(session, _id=0, folderPath=""):
        params = {
            "shareToken": shareToken,
            "pageSize": 1000,
            "pid": _id,
        }
        try:
            _json = session.get(
                "https://www.linkbox.to/api/file/share_out_list",
                params=params,
            ).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        data = _json["data"]
        if not data:
            if "msg" in _json:
                raise DirectDownloadLinkException(f"ERROR: {_json['msg']}")
            raise DirectDownloadLinkException("ERROR: data not found")
        try:
            if data["shareType"] == "singleItem":
                return __singleItem(session, data["itemId"])
        except Exception:
            pass
        if not details["title"]:
            details["title"] = data["dirName"]
        contents = data["list"]
        if not contents:
            return None
        for content in contents:
            if content["type"] == "dir" and "url" not in content:
                if not folderPath:
                    newFolderPath = ospath.join(details["title"], content["name"])
                else:
                    newFolderPath = ospath.join(folderPath, content["name"])
                if not details["title"]:
                    details["title"] = content["name"]
                __fetch_links(session, content["id"], newFolderPath)
            elif "url" in content:
                if not folderPath:
                    folderPath = details["title"]
                filename = content["name"]
                if (sub_type := content.get("sub_type")) and not filename.endswith(
                    sub_type,
                ):
                    filename += f".{sub_type}"
                item = {
                    "path": ospath.join(folderPath),
                    "filename": filename,
                    "url": content["url"],
                }
                if "size" in content:
                    size = content["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details["total_size"] += size
                details["contents"].append(item)
        return None

    try:
        with Session() as session:
            __fetch_links(session)
    except DirectDownloadLinkException as e:
        raise e
    return details


def gofile(url):
    try:
        if "::" in url:
            _password = url.split("::")[-1]
            _password = sha256(_password.encode("utf-8")).hexdigest()
            url = url.split("::")[-2]
        else:
            _password = ""
        _id = url.split("/")[-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")

    def __get_token(session):
        headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }
        __url = "https://api.gofile.io/accounts"
        try:
            __res = session.post(__url, headers=headers).json()
            if __res["status"] != "ok":
                raise DirectDownloadLinkException("ERROR: Failed to get token.")
            return __res["data"]["token"]
        except Exception as e:
            raise e

    def __fetch_links(session, _id, folderPath=""):
        _url = f"https://api.gofile.io/contents/{_id}?wt=4fd6sg89d7s6&cache=true"
        headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Authorization": "Bearer" + " " + token,
        }
        if _password:
            _url += f"&password={_password}"
        try:
            _json = session.get(_url, headers=headers).json()
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
        if _json["status"] in "error-passwordRequired":
            raise DirectDownloadLinkException(
                f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(url)}",
            )
        if _json["status"] in "error-passwordWrong":
            raise DirectDownloadLinkException("ERROR: This password is wrong !")
        if _json["status"] in "error-notFound":
            raise DirectDownloadLinkException(
                "ERROR: File not found on gofile's server",
            )
        if _json["status"] in "error-notPublic":
            raise DirectDownloadLinkException("ERROR: This folder is not public")

        data = _json["data"]

        if not details["title"]:
            details["title"] = data["name"] if data["type"] == "folder" else _id

        contents = data["children"]
        for content in contents.values():
            if content["type"] == "folder":
                if not content["public"]:
                    continue
                if not folderPath:
                    newFolderPath = ospath.join(details["title"], content["name"])
                else:
                    newFolderPath = ospath.join(folderPath, content["name"])
                __fetch_links(session, content["id"], newFolderPath)
            else:
                if not folderPath:
                    folderPath = details["title"]
                item = {
                    "path": ospath.join(folderPath),
                    "filename": content["name"],
                    "url": content["link"],
                }
                if "size" in content:
                    size = content["size"]
                    if isinstance(size, str) and size.isdigit():
                        size = float(size)
                    details["total_size"] += size
                details["contents"].append(item)

    details = {"contents": [], "title": "", "total_size": 0}
    with Session() as session:
        try:
            token = __get_token(session)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
        details["header"] = f"Cookie: accountToken={token}"
        try:
            __fetch_links(session, _id)
        except Exception as e:
            raise DirectDownloadLinkException(e)

    if len(details["contents"]) == 1:
        return (details["contents"][0]["url"], details["header"])
    return details


def cf_bypass(url):
    "DO NOT ABUSE THIS"
    try:
        data = {"cmd": "request.get", "url": url, "maxTimeout": 60000}
        _json = post(
            "https://cf.jmdkh.eu.org/v1",
            headers={"Content-Type": "application/json"},
            json=data,
        ).json()
        if _json["status"] == "ok":
            return _json["solution"]["response"]
    except Exception as e:
        e
    raise DirectDownloadLinkException("ERROR: Con't bypass cloudflare")


def send_cm_file(url, file_id=None):
    if "::" in url:
        _password = url.split("::")[-1]
        url = url.split("::")[-2]
    else:
        _password = ""
    _passwordNeed = False
    with create_scraper() as session:
        if file_id is None:
            try:
                html = HTML(session.get(url).text)
            except Exception as e:
                raise DirectDownloadLinkException(
                    f"ERROR: {e.__class__.__name__}",
                ) from e
            if html.xpath("//input[@name='password']"):
                _passwordNeed = True
            if not (file_id := html.xpath("//input[@name='id']/@value")):
                raise DirectDownloadLinkException("ERROR: file_id not found")
        try:
            data = {"op": "download2", "id": file_id}
            if _password and _passwordNeed:
                data["password"] = _password
            _res = session.post("https://send.cm/", data=data, allow_redirects=False)
            if "Location" in _res.headers:
                return (_res.headers["Location"], ["Referer: https://send.cm/"])
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        if _passwordNeed:
            raise DirectDownloadLinkException(
                f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(url)}",
            )
        raise DirectDownloadLinkException("ERROR: Direct link not found")


def send_cm(url):
    if "/d/" in url:
        return send_cm_file(url)
    if "/s/" not in url:
        file_id = url.split("/")[-1]
        return send_cm_file(url, file_id)
    splitted_url = url.split("/")
    details = {
        "contents": [],
        "title": "",
        "total_size": 0,
        "header": "Referer: https://send.cm/",
    }
    if len(splitted_url) == 5:
        url += "/"
        splitted_url = url.split("/")
    if len(splitted_url) >= 7:
        details["title"] = splitted_url[5]
    else:
        details["title"] = splitted_url[-1]
    session = Session()

    def __collectFolders(html):
        folders = []
        folders_urls = html.xpath("//h6/a/@href")
        folders_names = html.xpath("//h6/a/text()")
        for folders_url, folders_name in zip(
            folders_urls,
            folders_names,
            strict=False,
        ):
            folders.append(
                {
                    "folder_link": folders_url.strip(),
                    "folder_name": folders_name.strip(),
                },
            )
        return folders

    def __getFile_link(file_id):
        try:
            _res = session.post(
                "https://send.cm/",
                data={"op": "download2", "id": file_id},
                allow_redirects=False,
            )
            if "Location" in _res.headers:
                return _res.headers["Location"]
        except Exception:
            pass

    def __getFiles(html):
        files = []
        hrefs = html.xpath('//tr[@class="selectable"]//a/@href')
        file_names = html.xpath('//tr[@class="selectable"]//a/text()')
        sizes = html.xpath('//tr[@class="selectable"]//span/text()')
        for href, file_name, size_text in zip(
            hrefs,
            file_names,
            sizes,
            strict=False,
        ):
            files.append(
                {
                    "file_id": href.split("/")[-1],
                    "file_name": file_name.strip(),
                    "size": speed_string_to_bytes(size_text.strip()),
                },
            )
        return files

    def __writeContents(html_text, folderPath=""):
        folders = __collectFolders(html_text)
        for folder in folders:
            _html = HTML(cf_bypass(folder["folder_link"]))
            __writeContents(_html, ospath.join(folderPath, folder["folder_name"]))
        files = __getFiles(html_text)
        for file in files:
            if not (link := __getFile_link(file["file_id"])):
                continue
            item = {"url": link, "filename": file["filename"], "path": folderPath}
            details["total_size"] += file["size"]
            details["contents"].append(item)

    try:
        mainHtml = HTML(cf_bypass(url))
    except DirectDownloadLinkException as e:
        raise e
    except Exception as e:
        raise DirectDownloadLinkException(
            f"ERROR: {e.__class__.__name__} While getting mainHtml",
        )
    try:
        __writeContents(mainHtml, details["title"])
    except DirectDownloadLinkException as e:
        raise e
    except Exception as e:
        raise DirectDownloadLinkException(
            f"ERROR: {e.__class__.__name__} While writing Contents",
        )
    finally:
        session.close()
    if len(details["contents"]) == 1:
        return (details["contents"][0]["url"], [details["header"]])
    return details


def doods(url):
    if "/e/" in url:
        url = url.replace("/e/", "/d/")
    parsed_url = urlparse(url)
    with create_scraper() as session:
        try:
            html = HTML(session.get(url).text)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__} While fetching token link",
            ) from e
        if not (link := html.xpath("//div[@class='download-content']//a/@href")):
            raise DirectDownloadLinkException(
                "ERROR: Token Link not found or maybe not allow to download! open in browser.",
            )
        link = f"{parsed_url.scheme}://{parsed_url.hostname}{link[0]}"
        sleep(2)
        try:
            _res = session.get(link)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__} While fetching download link",
            ) from e
    if not (link := search(r"window\.open\('(\S+)'", _res.text)):
        raise DirectDownloadLinkException("ERROR: Download link not found try again")
    return (
        link.group(1),
        [f"Referer: {parsed_url.scheme}://{parsed_url.hostname}/"],
    )


def easyupload(url):
    if "::" in url:
        _password = url.split("::")[-1]
        url = url.split("::")[-2]
    else:
        _password = ""
    file_id = url.split("/")[-1]
    with create_scraper() as session:
        try:
            _res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")
        first_page_html = HTML(_res.text)
        if (
            first_page_html.xpath("//h6[contains(text(),'Password Protected')]")
            and not _password
        ):
            raise DirectDownloadLinkException(
                f"ERROR:\n{PASSWORD_ERROR_MESSAGE.format(url)}",
            )
        if not (
            match := search(
                r"https://eu(?:[1-9][0-9]?|100)\.easyupload\.io/action\.php",
                _res.text,
            )
        ):
            raise DirectDownloadLinkException(
                "ERROR: Failed to get server for EasyUpload Link",
            )
        action_url = match.group()
        session.headers.update({"referer": "https://easyupload.io/"})
        recaptcha_params = {
            "k": "6LfWajMdAAAAAGLXz_nxz2tHnuqa-abQqC97DIZ3",
            "ar": "1",
            "co": "aHR0cHM6Ly9lYXN5dXBsb2FkLmlvOjQ0Mw..",
            "hl": "en",
            "v": "0hCdE87LyjzAkFO5Ff-v7Hj1",
            "size": "invisible",
            "cb": "c3o1vbaxbmwe",
        }
        if not (captcha_token := get_captcha_token(session, recaptcha_params)):
            raise DirectDownloadLinkException("ERROR: Captcha token not found")
        try:
            data = {
                "type": "download-token",
                "url": file_id,
                "value": _password,
                "captchatoken": captcha_token,
                "method": "regular",
            }
            json_resp = session.post(url=action_url, data=data).json()
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    if "download_link" in json_resp:
        return json_resp["download_link"]
    if "data" in json_resp:
        raise DirectDownloadLinkException(
            f"ERROR: Failed to generate direct link due to {json_resp['data']}",
        )
    raise DirectDownloadLinkException(
        "ERROR: Failed to generate direct link from EasyUpload.",
    )


def filelions_and_streamwish(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    scheme = parsed_url.scheme
    if any(
        x in hostname
        for x in [
            "filelions.co",
            "filelions.live",
            "filelions.to",
            "filelions.site",
            "cabecabean.lol",
            "filelions.online",
            "mycloudz.cc",
        ]
    ):
        apiKey = Config.FILELION_API
        apiUrl = "https://vidhideapi.com"
    elif any(
        x in hostname
        for x in [
            "embedwish.com",
            "kissmovies.net",
            "kitabmarkaz.xyz",
            "wishfast.top",
            "streamwish.to",
        ]
    ):
        apiKey = Config.STREAMWISH_API
        apiUrl = "https://api.streamwish.com"
    if not apiKey:
        raise DirectDownloadLinkException(
            f"ERROR: API is not provided get it from {scheme}://{hostname}",
        )
    file_code = url.split("/")[-1]
    quality = ""
    if bool(file_code.endswith(("_o", "_h", "_n", "_l"))):
        spited_file_code = file_code.rsplit("_", 1)
        quality = spited_file_code[1]
        file_code = spited_file_code[0]
    url = f"{scheme}://{hostname}/{file_code}"
    try:
        _res = get(
            f"{apiUrl}/api/file/direct_link",
            params={"key": apiKey, "file_code": file_code, "hls": "1"},
        ).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    if _res["status"] != 200:
        raise DirectDownloadLinkException(f"ERROR: {_res['msg']}")
    result = _res["result"]
    if not result["versions"]:
        raise DirectDownloadLinkException("ERROR: File Not Found")
    error = "\nProvide a quality to download the video\nAvailable Quality:"
    for version in result["versions"]:
        if quality == version["name"]:
            return version["url"]
        if version["name"] == "l":
            error += "\nLow"
        elif version["name"] == "n":
            error += "\nNormal"
        elif version["name"] == "o":
            error += "\nOriginal"
        elif version["name"] == "h":
            error += "\nHD"
        error += f" <code>{url}_{version['name']}</code>"
    raise DirectDownloadLinkException(f"ERROR: {error}")


def streamvid(url: str):
    file_code = url.split("/")[-1]
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.hostname}/d/{file_code}"
    quality_defined = bool(url.endswith(("_o", "_h", "_n", "_l")))
    with create_scraper() as session:
        try:
            html = HTML(session.get(url).text)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        if quality_defined:
            data = {}
            if not (inputs := html.xpath('//form[@id="F1"]//input')):
                raise DirectDownloadLinkException("ERROR: No inputs found")
            for i in inputs:
                if key := i.get("name"):
                    data[key] = i.get("value")
            try:
                html = HTML(session.post(url, data=data).text)
            except Exception as e:
                raise DirectDownloadLinkException(
                    f"ERROR: {e.__class__.__name__}",
                ) from e
            if not (
                script := html.xpath(
                    '//script[contains(text(),"document.location.href")]/text()',
                )
            ):
                if error := html.xpath(
                    '//div[@class="alert alert-danger"][1]/text()[2]',
                ):
                    raise DirectDownloadLinkException(f"ERROR: {error[0]}")
                raise DirectDownloadLinkException(
                    "ERROR: direct link script not found!",
                )
            if directLink := findall(r'document\.location\.href="(.*)"', script[0]):
                return directLink[0]
            raise DirectDownloadLinkException(
                "ERROR: direct link not found! in the script",
            )
        if (qualities_urls := html.xpath('//div[@id="dl_versions"]/a/@href')) and (
            qualities := html.xpath('//div[@id="dl_versions"]/a/text()[2]')
        ):
            error = "\nProvide a quality to download the video\nAvailable Quality:"
            for quality_url, quality in zip(qualities_urls, qualities, strict=False):
                error += f"\n{quality.strip()} <code>{quality_url}</code>"
            raise DirectDownloadLinkException(f"ERROR: {error}")
        if error := html.xpath('//div[@class="not-found-text"]/text()'):
            raise DirectDownloadLinkException(f"ERROR: {error[0]}")
        raise DirectDownloadLinkException("ERROR: Something went wrong")


def streamhub(url):
    file_code = url.split("/")[-1]
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.hostname}/d/{file_code}"
    with create_scraper() as session:
        try:
            html = HTML(session.get(url).text)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        if not (inputs := html.xpath('//form[@name="F1"]//input')):
            raise DirectDownloadLinkException("ERROR: No inputs found")
        data = {}
        for i in inputs:
            if key := i.get("name"):
                data[key] = i.get("value")
        session.headers.update({"referer": url})
        sleep(1)
        try:
            html = HTML(session.post(url, data=data).text)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
        if directLink := html.xpath(
            '//a[@class="btn btn-primary btn-go downloadbtn"]/@href',
        ):
            return directLink[0]
        if error := html.xpath('//div[@class="alert alert-danger"]/text()[2]'):
            raise DirectDownloadLinkException(f"ERROR: {error[0]}")
        raise DirectDownloadLinkException("ERROR: direct link not found!")


def pcloud(url):
    with create_scraper() as session:
        try:
            res = session.get(url)
        except Exception as e:
            raise DirectDownloadLinkException(
                f"ERROR: {e.__class__.__name__}",
            ) from e
    if link := findall(r".downloadlink.:..(https:.*)..", res.text):
        return link[0].replace(r"\/", "/")
    raise DirectDownloadLinkException("ERROR: Direct link not found")


def tmpsend(url):
    parsed_url = urlparse(url)
    if any(x in parsed_url.path for x in ["thank-you", "download"]):
        query_params = parse_qs(parsed_url.query)
        if file_id := query_params.get("d"):
            file_id = file_id[0]
    elif not (file_id := parsed_url.path.strip("/")):
        raise DirectDownloadLinkException("ERROR: Invalid URL format")
    referer_url = f"https://tmpsend.com/thank-you?d={file_id}"
    header = [f"Referer: {referer_url}"]
    download_link = f"https://tmpsend.com/download?d={file_id}"
    return download_link, header


def qiwi(url):
    """qiwi.gg link generator
    based on https://github.com/aenulrofik"""
    file_id = url.split("/")[-1]
    try:
        res = get(url).text
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    tree = HTML(res)
    if name := tree.xpath('//h1[@class="page_TextHeading__VsM7r"]/text()'):
        ext = name[0].split(".")[-1]
        return f"https://spyderrock.com/{file_id}.{ext}"
    else:
        raise DirectDownloadLinkException("ERROR: File not found")


def mp4upload(url):
    with Session() as session:
        try:
            url = url.replace("embed-", "")
            req = session.get(url).text
            tree = HTML(req)
            inputs = tree.xpath("//input")
            header = ["Referer: https://www.mp4upload.com/"]
            data = {input.get("name"): input.get("value") for input in inputs}
            if not data:
                raise DirectDownloadLinkException("ERROR: File Not Found!")
            post = session.post(
                url,
                data=data,
                headers={
                    "User-Agent": user_agent,
                    "Referer": "https://www.mp4upload.com/",
                },
            ).text
            tree = HTML(post)
            inputs = tree.xpath('//form[@name="F1"]//input')
            data = {
                input.get("name"): input.get("value").replace(" ", "")
                for input in inputs
            }
            if not data:
                raise DirectDownloadLinkException("ERROR: File Not Found!")
            data["referer"] = url
            direct_link = session.post(url, data=data).url
            return direct_link, header
        except Exception:
            raise DirectDownloadLinkException("ERROR: File Not Found!")


def berkasdrive(url):
    """berkasdrive.com link generator
    by https://github.com/aenulrofik"""
    try:
        sesi = get(url).text
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}") from e
    html = HTML(sesi)
    if link := html.xpath("//script")[0].text.split('"')[1]:
        return b64decode(link).decode("utf-8")
    raise DirectDownloadLinkException("ERROR: File Not Found!")


def swisstransfer(link):
    matched_link = match(
        r"https://www\.swisstransfer\.com/d/([\w-]+)(?:\:\:(\w+))?", link
    )
    if not matched_link:
        raise DirectDownloadLinkException(
            f"ERROR: Invalid SwissTransfer link format {link}"
        )

    transfer_id, password = matched_link.groups()
    password = password or ""

    def encode_password(password):
        return (
            b64encode(password.encode("utf-8")).decode("utf-8") if password else ""
        )

    def getfile(transfer_id, password):
        url = f"https://www.swisstransfer.com/api/links/{transfer_id}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Authorization": encode_password(password) if password else "",
            "Content-Type": "application/json" if not password else "",
        }
        response = get(url, headers=headers)

        if response.status_code == 200:
            try:
                return response.json(), [
                    f"{k}: {v}" for k, v in headers.items() if v
                ]
            except ValueError:
                raise DirectDownloadLinkException(
                    f"ERROR: Error parsing JSON response {response.text}"
                )
        raise DirectDownloadLinkException(
            f"ERROR: Error fetching file details {response.status_code}, {response.text}"
        )

    def gettoken(password, containerUUID, fileUUID):
        url = "https://www.swisstransfer.com/api/generateDownloadToken"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json",
        }
        body = {
            "password": password,
            "containerUUID": containerUUID,
            "fileUUID": fileUUID,
        }

        response = post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.text.strip().replace('"', "")
        raise DirectDownloadLinkException(
            f"ERROR: Error generating download token {response.status_code}, {response.text}"
        )

    data, _ = getfile(transfer_id, password)
    if not data:
        return None

    try:
        container_uuid = data["data"]["containerUUID"]
        download_host = data["data"]["downloadHost"]
        files = data["data"]["container"]["files"]
        folder_name = data["data"]["container"]["message"] or "unknown"
    except (KeyError, IndexError, TypeError) as e:
        raise DirectDownloadLinkException(f"ERROR: Error parsing file details {e}")

    total_size = sum(file["fileSizeInBytes"] for file in files)

    if len(files) == 1:
        file = files[0]
        file_uuid = file["UUID"]
        token = gettoken(password, container_uuid, file_uuid)
        download_url = f"https://{download_host}/api/download/{transfer_id}/{file_uuid}?token={token}"
        return download_url, ["User-Agent:Mozilla/5.0"]

    contents = []
    for file in files:
        file_uuid = file["UUID"]
        file_name = file["fileName"]
        file_size = file["fileSizeInBytes"]

        token = gettoken(password, container_uuid, file_uuid)
        if not token:
            continue

        download_url = f"https://{download_host}/api/download/{transfer_id}/{file_uuid}?token={token}"
        contents.append({"filename": file_name, "path": "", "url": download_url})

    return {
        "contents": contents,
        "title": folder_name,
        "total_size": total_size,
        "header": "User-Agent:Mozilla/5.0",
    }


def instagram(link: str) -> str:
    """
    Fetches the direct video download URL from an Instagram post.

    Args:
        link (str): The Instagram post URL.

    Returns:
        str: The direct video URL.

    Raises:
        DirectDownloadLinkException: If any error occurs during the process.
    """
    if not Config.INSTADL_API:
        raise DirectDownloadLinkException(
            f"ERROR: Instagram downloader API not added, Try ytdl commands"
        )
    full_url = f"{Config.INSTADL_API}/api/video?postUrl={link}"

    try:
        response = get(full_url)
        response.raise_for_status()

        data = response.json()

        if (
            data.get("status") == "success"
            and "data" in data
            and "videoUrl" in data["data"]
        ):
            return data["data"]["videoUrl"]

        raise DirectDownloadLinkException("ERROR: Failed to retrieve video URL.")

    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")
