# -*- coding: utf-8 -*-
#
# 単語埋め込みベクトル（Word2Vec など）を行うための
# 1. テキストデータのゴミ取り
# 2. 分かち書き
# を行う。
#
# 2018.03.14 初期作成 伊藤友哉
# 2018.03.15 改定 富山
# 2018.03.16 改定 富山
#

import re
import mojimoji
import sys
import MeCab
import os
import time
import emoji
#from tqdm import tqdm


#
# ゴミ処理を行う。中国語除けない
#
def clean_text(text):  # ゴミ処理
    replaced_text = '\n'.join(s.strip() for s in text.splitlines()[
                              0:] if s != '')  # ヘッダーがあれば削除(このデータはしなくてよい)
    replaced_text = replaced_text.lower()
    replaced_text = re.sub(r'[■■●★◆◇▼♡]', '', replaced_text)
    replaced_text = re.sub(r'　', ' ', replaced_text)  # 全角空白の除去
    replaced_text = re.sub(r'[가-힣]*', '', replaced_text)  # ハングル削除
    replaced_text = re.sub(
        r'[0-9]+(時|分|年|月|日|秒|円|点|名|\/|:|-|\.)+[0-9]*', '', replaced_text)  # 数字表現を除去
    replaced_text = ''.join(
        c for c in replaced_text if c not in emoji.UNICODE_EMOJI)  # 　絵文字除去
    replaced_text = re.sub(r'[가-힣]*', '', replaced_text)  # ハングル削除
    replaced_text = re.sub(r'[{}]', '', replaced_text)  # {}の除去
    replaced_text = re.sub(r'\&?[lgr]t;?', '', replaced_text)  # rt, gt, ltの除去
    replaced_text = re.sub(r'[【】]', '', replaced_text)       # 【】の除去
    replaced_text = re.sub(r'[（）()]', '', replaced_text)     # （）の除去
    replaced_text = re.sub(r'[［］\[\]]', '', replaced_text)   # ［］の除去
    replaced_text = re.sub(r'[@＠]\w+', '', replaced_text)  # メンションの除去
    replaced_text = re.sub(r'[#][\w一-龥ぁ-んァ-ン]+', '', replaced_text)  # ハッシュタグの除去
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

    return replaced_text

#
# 中国語除去
#
def is_zh(in_str):
    """
    SJISに変換して文字数が減れば簡体字があるので中国語
    """
    return (set(in_str) - set(in_str.encode('sjis', 'ignore').decode('sjis'))) != set([])


#
# カタカナ半角を全角に, 数字英字全角を半角に
#
def zenkaku_hankaku(text):
    re = mojimoji.zen_to_han(text, kana=False)
    re = mojimoji.han_to_zen(re, digit=False, ascii=False)
    return re


#
# わかち書き　　　ストップワードの除去は行わない。
#
# ※　環境に合わせて、Neologdの格納ディレクトリを書き換えること
#
def wakati_by_mecab(text, form):
    #print("wakati_by_mecab")
    #print(form)
    #print(text)
    tagger = MeCab.Tagger('-d /usr/lib64/mecab/dic/mecab-ipadic-neologd')
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_list = []
    #print("koko")
    while node:
        pos = node.feature.split(",")[0]

        #print(pos)
        #print(form)

        #if pos in form_list:   # 対象とする品詞
        if pos in form:   # 対象とする品詞
            word = node.surface
            word_list.append(word)
        node = node.next

    return " ".join(word_list)


#
# わかち書き　　　ストップワードの除去も行う。
#
# ※　環境に合わせて、Neologdの格納ディレクトリを書き換えること
#
def wakati_mecab_remove_stopword(text, form):
    tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_list = []
    while node:
        pos = node.feature.split(",")[0]
        if pos in form:   # 対象とする品詞
            word = node.surface
            word_list.append(word)
        node = node.next

    # ストップワードを除去
    # ストップワードリスト
    stopwords = create_stopwords(get_stopword_path())
    word_list = [word for word in word_list if word not in stopwords]

    return " ".join(word_list)



#
# ストップワードテキストファイルのパスの取得
# ※このプログラムと同じディレクトリに保管してください
#
def get_stopword_path():
    name = os.path.dirname(os.path.abspath(__name__))
    joined_path = os.path.join(name, './stopwords.txt')
    data_path = os.path.normpath(joined_path)
    return data_path


#
# ストップワードのリスト(stopwords)作成
#
def create_stopwords(file_path):
    stopwords = []
    for w in open(file_path, "r"):
        w = w.replace('\n', '')
        if len(w) > 0:
            stopwords.append(w)
    return stopwords


#
# ストップワード除去
#
def remove_stopwords(words, stopwords):
    #print(words)
    words = [word for word in words if word not in stopwords]
    print(words)
    #return "".join(words)


#
# 実行プログラム
#

#form_list = ["名詞", "動詞", "形容詞", "感動詞", "副詞", "助詞","記号", "接頭詞", "助動詞", "連体詞", "フィラー", "その他"]

t1 = time.time()
print("処理開始しました")

form_option = [
    ["名詞", "動詞", "形容詞"],
    ["名詞", "動詞", "形容詞", "感動詞", "副詞", "助詞", "記号", "接頭詞", "助動詞", "連体詞", "フィラー", "その他"],
    ["名詞"],
    ["名詞", "動詞", "形容詞", "感動詞", "副詞", "助詞", "接頭詞", "助動詞", "連体詞", "フィラー", "その他"]
]

#output_file_dir = "./wakati_data/"
output_file_dir = "./"

output_file_suffix = [
              "nva",
              "all",
              "noun",
              "all_without_kigou"
              ]


media = [
         #"naver",
         #"yahoo",
         # "twitter",
         "sample"
        ]

input_file = [
              #"./rawdata/naver.txt",
              #"./rawdata/yahoo.txt",
              # "./rawdata/twitter.txt",
              "./rawdata/sample.txt",
             ]


# ストップワードリストの取得
#
stopwords = create_stopwords(get_stopword_path())
# print(stopwords)

for (md, ifile) in zip(media, input_file):

    for (form, ofile_suffix) in zip(form_option, output_file_suffix):

        print(media)
        print(form)
        #form_list = form_option[n_list]

        f = open(ifile, "r")
        line = f.readline()

        ofile = output_file_dir + md + "_" + ofile_suffix + "_wakati.txt"
        fw = open(ofile, "w")

        while line:
            if len(line) < 10:
                line = f.readline()
                continue
            if is_zh(line):  # 中国語の文章はスキップ
                line = f.readline()
                continue
            line = clean_text(line)
            line = zenkaku_hankaku(line)

            fw.write(wakati_mecab_remove_stopword(line, form) + "\n")

            line = f.readline()


        f.close
        fw.close

        #text = clean_text(text)
        #text = zenkaku_hankaku(text)

        #text = wakati_by_mecab(text, form)

        #lines = text.splitlines()
        #del text
        #text = ""
        #for line in lines:
        #    update_line = wakati_by_mecab(line, form) + "\n"
        #    text = text + update_line
        #
        #text = remove_stopwords(text, stopwords)

        #for line in lines:
        #    update_line = wakati_mecab_remove_stopword(line, form) + "\n"
        #    text = text + update_line



t2 = time.time()
elapsed_time = t2 - t1
print("処理が終了しました。実行時間は " + str(elapsed_time) + " 秒でした")
