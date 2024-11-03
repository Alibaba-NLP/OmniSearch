from nltk.tokenize import word_tokenize
import re
import sys
import jieba
from collections import Counter
from tqdm import tqdm
import json, argparse

contractions = {
            'aint': "ain't",
            'arent': "aren't",
            'cant': "can't",
            'couldve': "could've",
            'couldnt': "couldn't",
            "couldn'tve": "couldn't've",
            "couldnt've": "couldn't've",
            'didnt': "didn't",
            'doesnt': "doesn't",
            'dont': "don't",
            'hadnt': "hadn't",
            "hadnt've": "hadn't've",
            "hadn'tve": "hadn't've",
            'hasnt': "hasn't",
            'havent': "haven't",
            'hed': "he'd",
            "hed've": "he'd've",
            "he'dve": "he'd've",
            'hes': "he's",
            'howd': "how'd",
            'howll': "how'll",
            'hows': "how's",
            "Id've": "I'd've",
            "I'dve": "I'd've",
            'Im': "I'm",
            'Ive': "I've",
            'isnt': "isn't",
            'itd': "it'd",
            "itd've": "it'd've",
            "it'dve": "it'd've",
            'itll': "it'll",
            "let's": "let's",
            'maam': "ma'am",
            'mightnt': "mightn't",
            "mightnt've": "mightn't've",
            "mightn'tve": "mightn't've",
            'mightve': "might've",
            'mustnt': "mustn't",
            'mustve': "must've",
            'neednt': "needn't",
            'notve': "not've",
            'oclock': "o'clock",
            'oughtnt': "oughtn't",
            "ow's'at": "'ow's'at",
            "'ows'at": "'ow's'at",
            "'ow'sat": "'ow's'at",
            'shant': "shan't",
            "shed've": "she'd've",
            "she'dve": "she'd've",
            "she's": "she's",
            'shouldve': "should've",
            'shouldnt': "shouldn't",
            "shouldnt've": "shouldn't've",
            "shouldn'tve": "shouldn't've",
            "somebody'd": 'somebodyd',
            "somebodyd've": "somebody'd've",
            "somebody'dve": "somebody'd've",
            'somebodyll': "somebody'll",
            'somebodys': "somebody's",
            'someoned': "someone'd",
            "someoned've": "someone'd've",
            "someone'dve": "someone'd've",
            'someonell': "someone'll",
            'someones': "someone's",
            'somethingd': "something'd",
            "somethingd've": "something'd've",
            "something'dve": "something'd've",
            'somethingll': "something'll",
            'thats': "that's",
            'thered': "there'd",
            "thered've": "there'd've",
            "there'dve": "there'd've",
            'therere': "there're",
            'theres': "there's",
            'theyd': "they'd",
            "theyd've": "they'd've",
            "they'dve": "they'd've",
            'theyll': "they'll",
            'theyre': "they're",
            'theyve': "they've",
            'twas': "'twas",
            'wasnt': "wasn't",
            "wed've": "we'd've",
            "we'dve": "we'd've",
            'weve': "we've",
            'werent': "weren't",
            'whatll': "what'll",
            'whatre': "what're",
            'whats': "what's",
            'whatve': "what've",
            'whens': "when's",
            'whered': "where'd",
            'wheres': "where's",
            'whereve': "where've",
            'whod': "who'd",
            "whod've": "who'd've",
            "who'dve": "who'd've",
            'wholl': "who'll",
            'whos': "who's",
            'whove': "who've",
            'whyll': "why'll",
            'whyre': "why're",
            'whys': "why's",
            'wont': "won't",
            'wouldve': "would've",
            'wouldnt': "wouldn't",
            "wouldnt've": "wouldn't've",
            "wouldn'tve": "wouldn't've",
            'yall': "y'all",
            "yall'll": "y'all'll",
            "y'allll": "y'all'll",
            "yall'd've": "y'all'd've",
            "y'alld've": "y'all'd've",
            "y'all'dve": "y'all'd've",
            'youd': "you'd",
            "youd've": "you'd've",
            "you'dve": "you'd've",
            'youll': "you'll",
            'youre': "you're",
            'youve': "you've",
        }

manualMap = {
            'none': '0',
            'zero': '0',
            'one': '1',
            'two': '2',
            'three': '3',
            'four': '4',
            'five': '5',
            'six': '6',
            'seven': '7',
            'eight': '8',
            'nine': '9',
            'ten': '10',
        }

articles = ['a', 'an', 'the']

periodStrip = re.compile('(?!<=\d)(\.)(?!\d)')

commaStrip = re.compile('(\d)(,)(\d)')

punct = [
            ';',
            r'/',
            '[',
            ']',
            '"',
            '{',
            '}',
            '(',
            ')',
            '=',
            '+',
            '\\',
            '_',
            '-',
            '>',
            '<',
            '@',
            '`',
            ',',
            '?',
            '!',
        ]

parser = argparse.ArgumentParser(description="")
parser.add_argument('--evaluate_file_path', default='')
parser.add_argument('--lang', default='en')
args = parser.parse_args()

def process_string(s):
    s = str(s)
    words = []
    for word in ' '.join(jieba.cut(s)).split():
        if word not in '，、。 ,.《》':
            words.append(word)
    return words

def process_string_en(s):
    s = str(s).lower()
    words = []
    for word in word_tokenize(s):
        if word not in ',.?!:;\'"':
            words.append(word)
    return words

def compute_acc_single(gold_toks, pred_toks):
    common = Counter(gold_toks) & Counter(pred_toks)
    num_same = sum(common.values())
    if len(gold_toks) == 0 or len(pred_toks) == 0:
        return float(gold_toks == pred_toks)
    if num_same == 0:
        return 0
    return num_same / len(gold_toks)

def compute_acc(a_golds, a_pred, lang):
    if lang == 'zh':
        if a_pred == '':
            return 0
        golds_toks = [process_string(a_gold) for a_gold in a_golds]
        pred_toks = process_string(a_pred)
    elif lang == 'en':
        if a_pred == '':
            return 0
        golds_toks = [process_string_en(a_gold) for a_gold in a_golds]
        pred_toks = process_string_en(a_pred)

    return max(
        compute_acc_single(gold_toks, pred_toks) for gold_toks in golds_toks)

def processPunctuation(inText):
    outText = inText
    for p in punct:
        if (p + ' ' in inText or ' ' + p
                in inText) or (re.search(commaStrip, inText) != None):
            outText = outText.replace(p, '')
        else:
            outText = outText.replace(p, ' ')
    outText = periodStrip.sub('', outText, re.UNICODE)
    return outText

def processDigitArticle(inText):
    outText = []
    tempText = inText.lower().split()
    for word in tempText:
        word = manualMap.setdefault(word, word)
        if word not in articles:
            outText.append(word)
        else:
            pass
    for wordId, word in enumerate(outText):
        if word in contractions:
            outText[wordId] = contractions[word]
    outText = ' '.join(outText)
    return outText

evaluate_file_path = args.evaluate_file_path

acc_list = []
f = open(evaluate_file_path, 'r')
for idd, line in enumerate(f.readlines()):
    data = json.loads(line)
    resAns = data['prediction']
    resAns = resAns.replace('\n', ' ')
    resAns = resAns.replace('\t', ' ')
    resAns = resAns.strip()
    resAns = processPunctuation(resAns)
    resAns = processDigitArticle(resAns)

    gtAnswers = data['answer']
    avgGTAcc = compute_acc(a_golds=gtAnswers, a_pred=resAns, lang=args.lang)
    acc_list.append(avgGTAcc)

print('Token F1-Recall: ', round(100 * float(sum(acc_list)) / len(acc_list), 2))

