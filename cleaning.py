import re
import mojimoji
import sys
import MeCab
from gensim import corpora
import os
import time
from tqdm import tqdm
from time import sleep


def clean_text(text):  # ゴミ処理, 中国語除けない
    replaced_text = '\n'.join(s.strip() for s in text.splitlines()[
                              0:] if s != '')  # ヘッダーがあれば削除(このデータはしなくてよい)
    replaced_text = replaced_text.lower()
    replaced_text = re.sub(r'[■■●★◆◇▼♡]', ' ', replaced_text)
    replaced_text = re.sub(r'[0-9]*(時|分|年|月|日|秒|円)', '', replaced_text)  # 注意！
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


def zenkaku_hankaku(text):  # カタカナ半角を全角に, 数字英字全角を半角に
    re = mojimoji.zen_to_han(text, kana=False)
    re = mojimoji.han_to_zen(re, digit=False, ascii=False)
    return re


def wakati_by_mecab(text):  # mecabで分かち書きする
    tagger = MeCab.Tagger('')
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_list = []
    while node:
        pos = node.feature.split(",")[0]
        if pos in form_list:   # 対象とする品詞
            word = node.surface
            word_list.append(word)
        node = node.next
    return " ".join(word_list)

# Neologdの入れ方。Neologdの辞書ファイル(自分は/usr/local/lib/mecab/dic/mecab-ipadic-neologdにあった。)をmecabrc(自分は/usr/local/etc/mecabrcにあった)
# の辞書参照箇所にコピーする。(該当箇所はdicdir =  /usr/local/lib/mecab/dic/mecab-ipadic-neologd)。注意点はターミナル起動直後よりも上の階層にいくから、気が付きづらい場所にあること。


def get_stopword_path():  # ストップワードのパスを取得。ストップワードテキストファイルはこのプログラムと同じディレクトリに保管してください
    name = os.path.dirname(os.path.abspath(__name__))
    joined_path = os.path.join(name, './stopwords.txt')
    data_path = os.path.normpath(joined_path)
    return data_path


def create_stopwords(file_path):  # ストップワードのリスト(stopwords)作成
    stopwords = []
    for w in open(file_path, "r"):
        w = w.replace('\n', '')
        if len(w) > 0:
            stopwords.append(w)
    return stopwords


def wakati_mecab_remove_stopword(text):  # Mecab & ストップワード除去
    tagger = MeCab.Tagger('')
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_list = []
    while node:
        pos = node.feature.split(",")[0]
        if pos in form_list:   # 対象とする品詞
            word = node.surface
            word_list.append(word)
        node = node.next
    # ここでストップワードを除去します
    # ストップワードリスト
    stopwords = create_stopwords(get_stopword_path())
    word_list = [word for word in word_list if word not in stopwords]
    return " ".join(word_list)


# 実行する

t1 = time.time()
print("処理開始しました")

big_form_list = [
    ["名詞", "動詞", "形容詞"],
    ["名詞", "動詞", "形容詞", "感動詞", "副詞", "助詞", "記号",
        "接頭詞", "助動詞", "連体詞", "フィラー", "その他"],
    ["名詞"],
    ["名詞", "動詞", "形容詞", "感動詞", "副詞", "助詞", "接頭詞", "助動詞", "連体詞", "フィラー", "その他"]
]

input_file = ["./rawdata/sample.txt",
              "./rawdata/twitter.txt", "./rawdata/yahoo.txt"]
output_file = ["./wakati_data/sample_nva.txt", "./wakati_data/sample_allform_wakati.txt",
               "./wakati_data/sample_noun_wakati.txt", "./wakati_data/sample_without_kigou_wakati.txt"]

for n_list in tqdm(range(len(big_form_list))):
    sleep(0.1)
    form_list = big_form_list[n_list]
    f = open(input_file[0], "r")  # TODO:input_fileをforで回す。
    fw = open(output_file[n_list], "w")

    text = f.readline()

    while text:
        if len(text) < 10:
            text = f.readline()
            continue

        text = clean_text(text)
        text = zenkaku_hankaku(text)
        # text = wakati_by_mecab(text) #ストップワード除去をしたくない場合はこちらをつかってください。
        text = wakati_mecab_remove_stopword(text)
        fw.write(text + "\n")
        text = f.readline()

    f.close
    fw.close

t2 = time.time()
elapsed_time = t2 - t1

print(f"処理が終了しました。実行時間は{elapsed_time}秒でした")
