import unicodedata
from collections import defaultdict
import unicodedata


#UnicodeのSymbol Otherを抽出しています

# reference: http://www.fileformat.info/info/unicode/category/index.htm
category_meanings = {
    'Cc' : 'Other, Control',
    'Cf' : 'Other, Format',
    'Cn' : 'Other, Not Assigned (no characters in the file have this property)',
    'Co' : 'Other, Private Use',
    'Cs' : 'Other, Surrogate',
    'LC' : 'Letter, Cased',
    'Ll' : 'Letter, Lowercase',
    'Lm' : 'Letter, Modifier',
    'Lo' : 'Letter, Other',
    'Lt' : 'Letter, Titlecase',
    'Lu' : 'Letter, Uppercase',
    'Mc' : 'Mark, Spacing Combining',
    'Me' : 'Mark, Enclosing',
    'Mn' : 'Mark, Nonspacing',
    'Nd' : 'Number, Decimal Digit',
    'Nl' : 'Number, Letter',
    'No' : 'Number, Other',
    'Pc' : 'Punctuation, Connector',
    'Pd' : 'Punctuation, Dash',
    'Pe' : 'Punctuation, Close',
    'Pf' : 'Punctuation, Final quote (may behave like Ps or Pe depending on usage)',
    'Pi' : 'Punctuation, Initial quote (may behave like Ps or Pe depending on usage)',
    'Po' : 'Punctuation, Other',
    'Ps' : 'Punctuation, Open',
    'Sc' : 'Symbol, Currency',
    'Sk' : 'Symbol, Modifier',
    'Sm' : 'Symbol, Math',
    'So' : 'Symbol, Other',
    'Zl' : 'Separator, Line',
    'Zp' : 'Separator, Paragraph',
    'Zs' : 'Separator, Space'
}

category_to_chars = defaultdict(list)
for i in range(0, 0x110000):
    ch = chr(i)
    category = unicodedata.category(ch)
    category_to_chars[category].append(ch)

for category in sorted(category_to_chars, key=lambda x: -len(category_to_chars[x])):
    print("{} ({}): {}".format(
        category,
        category_meanings[category],
        len(category_to_chars[category])))

CHAR_PER_LINE = 50
for i, ch in enumerate(category_to_chars['So']):
    print(ch, end="")
    if (i + 1) % CHAR_PER_LINE == 0:
        print("<br>")
