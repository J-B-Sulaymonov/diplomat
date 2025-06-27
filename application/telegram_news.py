import json
import requests
from application.models import News_img

def send_telegram_news(name, short_info, id):
    token = '7346977694:AAHTzeEbX0sDwckJGPzURp9bAk2I1X6Naw0'
    #chat_id = '@ciscnews'
    chat_id = '@test'
    news_imgs = News_img.objects.filter(news_id=id)[:5] 

    detail_link = (
        f"<b>Батафсил — </b><a href='https://cisc.uz/ky/news-item/{id}/'>cisc.uz</a>\n\n"
        f"<b>Ислом цивилизацияси маркази Ахборот хизмати</b>"
    )
    socials = (
        "\n\n"
        "| <a href='https://t.me/islommarkazi'>Telegram</a> "
        "| <a href='https://www.youtube.com/watch?v=GzicN3FaUj8'>YouTube</a> "
        "| <a href='https://www.instagram.com/sivilizatsiya__markazi/?img_index=1'>Instagram</a> "
        "| <a href='https://www.facebook.com/CentrofIslamiccivilizationinUzbekistan'>Facebook</a> "
        "| <a href='https://cisc.uz/'>cisc.uz</a> |"
    )
    caption = f"<b>{name}</b>\n\n{short_info}\n\n{detail_link}{socials}"

    media = []
    files = {}

    for i, img in enumerate(news_imgs):
        file_path = img.img.path
        file_name = f"photo{i}.jpg"

        files[file_name] = open(file_path, 'rb')

        media_item = {
            "type": "photo",
            "media": f"attach://{file_name}"
        }

        if i == 0:
            media_item["caption"] = caption
            media_item["parse_mode"] = "HTML"

        media.append(media_item)

    url = f"https://api.telegram.org/bot{token}/sendMediaGroup"

    try:
        response = requests.post(url, data={'chat_id': chat_id, 'media': json.dumps(media)}, files=files)
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        for f in files.values():
            f.close()
    #
