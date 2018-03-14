import re
import mojimoji
import sys
import MeCab
import os

# ゴミ処理
# TODO: 日本語英語以外除去(ハングルDone! 中国語は漢字とかぶるからムリポ)


def clean_text(text):
    replaced_text = '\n'.join(s.strip() for s in text.splitlines()[
                              0:] if s != '')  # ヘッダーがあれば削除(このデータはしなくてよい)
    replaced_text = replaced_text.lower()
    replaced_text = re.sub(r'[■■●★◆◇▼♡]', ' ', replaced_text)
    replaced_text = re.sub(r'.?[0-9](時|分)', '', replaced_text)
    replaced_text = re.sub(r'[{}]', ' ', replaced_text)
    replaced_text = re.sub(r'\&[lgr]t;', ' ', replaced_text)
    replaced_text = re.sub(r'[【】]', ' ', replaced_text)       # 【】の除去
    replaced_text = re.sub(r'[（）()]', ' ', replaced_text)     # （）の除去
    replaced_text = re.sub(r'[［］\[\]]', ' ', replaced_text)   # ［］の除去
    replaced_text = re.sub(r'[@＠]\w+', '', replaced_text)  # メンションの除去
    replaced_text = re.sub(r'[#][\w一-龥ぁ-んァ-ン]+', '',
                           replaced_text)  # ハッシュタグの除去
    replaced_text = re.sub(r'https?:\/\/.*', '', replaced_text)  # URLの除去
    replaced_text = re.sub(r'pic\.twitter\.com\/.*', '',
                           replaced_text)  # pic.twitter.com/の除去
    replaced_text = re.sub(r'\.?twitter\.com\/.*', '',
                           replaced_text)  # .twitter.com/の除去
    replaced_text = re.sub(r'instagram\.com\/.*', '',
                           replaced_text)  # instagram.com/の除去
    replaced_text = re.sub(r'fashion-press\.net\/.*', '', replaced_text)
    replaced_text = re.sub(r'cookpad\.com\/.*', ' ', replaced_text)
    replaced_text = re.sub(r'news\.livedoor\.com\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.com\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.net\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.co\.jp\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.jp\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.it\/.*', '', replaced_text)
    replaced_text = re.sub(r'youtu\.be\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.me\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.mu|\.jp\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.jp\/.*', '', replaced_text)
    replaced_text = re.sub(r'\.ly\/.*', '', replaced_text)
    replaced_text = re.sub(
        r'(news|blog|fc2|headlines|link)(\.|\/).*', '', replaced_text)
    replaced_text = re.sub(r'([a-z]\&)?(amp|mp);[a-z]', '', replaced_text)
    replaced_text = re.sub(r'写真=.*', '', replaced_text)
    replaced_text = re.sub(r'　', ' ', replaced_text)  # 全角空白の除去
    replaced_text = re.sub(r'[가-힣]*', '', replaced_text)  # ハングル削除
    return replaced_text

# カタカナ半角を全角に
# 数字英字全角を半角に


def zenkaku_hankaku(text):
    re = mojimoji.zen_to_han(text, kana=False)
    re = mojimoji.han_to_zen(re, digit=False, ascii=False)
    return re

# 分かち書き(Mecab, Neologd)
# TODO: サーバー上でどうやってNeologd入れる？？


def wakati_nva_by_mecab(text):
    tagger = MeCab.Tagger('')
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_list = []
    while node:
        pos = node.feature.split(",")[0]
        # node.future = {名詞: 1,動詞: 2,形容詞: 3,副詞: 4,助詞: 5,接続詞: 6,助動詞: 7,連体詞: 8,感動詞: 9}
        # 記号、感動詞など除けばノイズは減るか？？
        if pos in ["名詞", "動詞", "形容詞"]:   # 対象とする品詞を変えたい場合はここをいじる
            word = node.surface
            word_list.append(word)
        node = node.next
    return " ".join(word_list)

# 普通の分かち書き


def wakati_by_mecab(text):
    tagger = MeCab.Tagger('')
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_list = []
    while node:
        word = node.surface
        word_list.append(word)
        node = node.next
    return " ".join(word_list)

# ストップワードテキストファイルはこのプログラムと同じディレクトリに保管してください


def get_stopword_path():
    name = os.path.dirname(os.path.abspath(__name__))
    joined_path = os.path.join(name, './stopwords.txt')
    data_path = os.path.normpath(joined_path)
    return data_path

# ストップワードのリスト(stopwords)作成


def create_stopwords(file_path):
    stopwords = []
    for w in open(file_path, "r"):
        w = w.replace('\n', '')
        if len(w) > 0:
            stopwords.append(w)
    return stopwords


# ストップワード除去


def remove_stopwords(words, stopwords):
    words = [word for word in words if word not in stopwords]
    return words



# ストップワードリスト
stopwords = create_stopwords(get_stopword_path())

#Mecabためし
text="まじでびっくりした！！!!"
tagger = MeCab.Tagger('')
tagger.parse('')
node = tagger.parseToNode(text)
word_list = []
while node:
    pos = node.feature.split(",")[0]
    # node.future = {名詞: 1,動詞: 2,形容詞: 3,副詞: 4,助詞: 5,接続詞: 6,助動詞: 7,連体詞: 8,感動詞: 9}
    # 記号、感動詞など除けばノイズは減るか？？
    if pos in ["名詞", "動詞", "形容詞"]:   # 対象とする品詞を変えたい場合はここをいじる
        word = node.surface
        word_list.append(word)
    print(pos)
    node = node.next
