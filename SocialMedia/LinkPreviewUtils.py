from urllib.error import URLError

from bs4 import BeautifulSoup
import urllib.request  as urlrequest


def link_preview(url):
    response_data = {}
    # Error 503 : Problème de connexion
    # Error 500 lien impossible à trouver

    try:
        soup = BeautifulSoup(urlrequest.urlopen(url), features="html.parser")
    except URLError:
        response_data['error'] = 503
        print("error 503 1")
        return response_data
    except ValueError:
        url = "http://" + url
        try:
            soup = BeautifulSoup(urlrequest.urlopen(url), features="html.parser")
        except URLError:
            response_data['error'] = 503
            print("error 503 2")
            return response_data
        except ValueError:
            response_data['error'] = 500
            return response_data


    # Title Fetch
    try:
        title = soup.title.contents[0]
    except Exception:
        title = url

    # Description  Fetch
    try:
        description = soup.find("meta", name="description", content=True)['content']
    except Exception:
        try:
            description = soup.find("meta", property="og:description", content=True)['content']
        except Exception:
            description = url

    # Icon Fetch
    try:
        icon_link = soup.find("link", rel="icon")['href']
    except Exception:
        try:
            icon_link = soup.find("link", rel="shortcut icon")['href']
        except Exception:
            icon_link = None

    # s'il accède à l'url de l'icone directement alors l'url est sous forme : http://url.com
    try:
        icon = urlrequest.urlopen(icon_link)
        icon = icon_link
    except Exception:
        # sinon c'est un url   static et   on y ajouter l'url au debut
        try:
            icon = urlrequest.urlopen(url + icon_link)
            icon = url + icon_link
        except  Exception:
            icon = None

    response_data['title'] = title
    response_data['description'] = description
    response_data['icon'] = icon
    response_data['url'] = url

    #  Dans la response a  la  request ajax faire : link_preview_data =  link_preview(url)
    # return JsonResponse(link_preview_data)

    return response_data
