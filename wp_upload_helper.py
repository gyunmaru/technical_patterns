# %%
from datetime import datetime
from urllib.parse import urljoin
import base64
import requests
import json

# %%


def header(user, password):
    credentials = user + ':' + password
    token = base64.b64encode(credentials.encode())
    header_json = {'Authorization': 'Basic ' + token.decode('utf-8')}
    return header_json

# %%


def upload_image_to_wordpress(file_path, url, header_json):
    media = {'file': open(file_path, "rb"), 'caption': 'My great demo picture'}
    responce = requests.post(url + "wp-json/wp/v2/media",
                             headers=header_json, files=media)
    return(responce)


# %%

# coding=utf-8
# WordPressのデータ
def post_article(
    url, user, passwd,
    status, slug, title, content,
    category_ids=[], tag_ids=[], media_id=None
):
    """
    記事を投稿して成功した場合はTrue、失敗した場合はFalseを返します。
    :param status: 記事の状態（公開:publish, 下書き:draft）
    :param slug: 記事識別子。URLの一部になる（ex. slug=aaa-bbb/ccc -> https://wordpress-example.com/aaa-bbb/ccc）
    :param title: 記事のタイトル
    :param content: 記事の本文
    :param category_ids: 記事に付与するカテゴリIDのリスト
    :param tag_ids: 記事に付与するタグIDのリスト
    :param media_id: 見出し画像のID
    :return: レスポンス
    """
    # credential and attributes
    user_ = user
    pass_ = passwd
    # build request body
    payload = {"status": status,
               "slug": slug,
               "title": title,
               "content": content,
               "date": datetime.now().isoformat(),
               "categories": category_ids,
               "tags": tag_ids}
    if media_id is not None:
        payload['featured_media'] = media_id
    # send POST request
    res = requests.post(urljoin(url, "wp-json/wp/v2/posts"),
                        data=json.dumps(payload),
                        headers={'Content-type': "application/json"},
                        auth=(user_, pass_))
    print('----------\n件名:「{}」の投稿リクエスト結果:{} res.status: {}'.format(
        title, res, repr(res.status_code)))
    return res

# %%


if __name__ == "__main__":

    with open('info.json', 'rb') as f:
        info_ = json.load(f)

    hed = header(info_['usr'], info_['ps'])
    upload_image_to_wordpress(
        './graph_html/8001_20220114.html', info_['url'], hed)

    # 記事を下書き投稿する（'draft'ではなく、'publish'にすれば公開投稿できます。）
    post_article('draft', 'test-api-post', 'テストタイトルだよ', 'テスト本文だよ',
                 category_ids=[], tag_ids=[], media_id=None)
