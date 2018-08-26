"""

3 class:	Location, Person, Organization
4 class:	Location, Person, Organization, Misc
7 class:	Location, Person, Organization, Money, Percent, Date, Time

only want stanford-ner jars and files

final output:
7 class:	Location, Person, Organization, Money, Percent, Date, Time
Location, Person, Organization, Money, Percent, Date, Time, Original_Text, URL
"""

import codecs
import csv
from collections import defaultdict
import logging
import multiprocessing as mp
import re
from time import time

import pandas as pd

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

# also 3 and 4 classes available. check /usr/local/share/stanford-ner-2018-02-27
MODEL_7_CLASSES_PATH = '/usr/local/share/stanford-ner-2018-02-27/classifiers/english.muc.7class.distsim.crf.ser.gz'
NER_JAR_PATH = '/usr/local/share/stanford-ner-2018-02-27/stanford-ner.jar'

RE_SERIES = re.compile(r'series [A-Z]{1}', re.I)

# create NER object
st = StanfordNERTagger(
    MODEL_7_CLASSES_PATH,
    NER_JAR_PATH,
    encoding='utf-8'
)


def classify_worker(summary):
    """
    extract Named Entities from a string of text
    :param summary: string of text
    :return: dictionary of Named Entity key value pairs. Ex: {'ORGANIZATION': 'Amazon', 'LOCATION': 'Seattle'}
    """
    url, text = summary
    text = text.strip()
    # Good news! multiprocessing can use st object defined outside worker
    tokenized_text = word_tokenize(text)
    classified_text = st.tag(tokenized_text)

    # TODO: separate tags linked to different entities. Ex: Google buys Amazon --> ORGANIZATION: Google | Amazon
    # Need to test
    output = defaultdict(list)
    current_tag = classified_text[0][1]
    for word, tag in classified_text:
        if tag in ('ORGANIZATION',) and tag in output and tag != current_tag:
            # new tag - separate and change tags
            output[tag].append('|')  # append separator
            current_tag = tag  # reset current_tag
        output[tag].append(word)

    # convert list of tags to string of tags
    output2 = dict()
    for k, v in output.items():
        if k in ('ORGANIZATION', 'LOCATION', 'O', 'PERSON'):
            output2[k] = ' '.join(v)
        else:
            output2[k] = ''.join(v)

    m = re.search(RE_SERIES, text)
    if m:
        output2['SERIES'] = m.group()
    else:
        output2['SERIES'] = ''

    output2['URL'] = url
    output2['TEXT'] = text

    logging.debug("location: {} --- {}".format(output2.get('LOCATION', ''), text))
    return output2


def classify_wrapper(summaries, filename):

    cpu_count = mp.cpu_count()
    logging.info('cpu_count: {}'.format(cpu_count))
    pool = mp.Pool(processes=cpu_count // 2)
    list_of_dicts = pool.map(classify_worker, summaries)
    pool.close()
    # TODO: write to the file in stream rather batch, so you don't risk losing everything on one job? Note order doesn't matter for writing...
    df = pd.DataFrame(list_of_dicts)
    df.rename(columns={'O': 'OTHER TAGS'})
    df.to_csv(filename, index=False,
              columns=['ORGANIZATION', 'LOCATION', 'SERIES', 'MONEY', 'DATE', 'TEXT', 'URL', 'PERSON', 'OTHER TAGS'])

if __name__ == '__main__':

    log_file = 'ner2.log'
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format="%s(asctime)s %(levelname)s %(name)s L%(lineno)d %(funcName)s: %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p')

    FINSMES_FILE_PATH_PATTERN = 'finsmes/files/page-{}.csv'
    output_filename = 'small_test.csv'
    summaries = []
    with codecs.open(FINSMES_FILE_PATH_PATTERN.format(0), 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            summaries.append(row)
    # skip page-1, doesn't exist
    for i in range(2, 1816):

        with codecs.open(FINSMES_FILE_PATH_PATTERN.format(i), 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                summaries.append(row)

    # get rid of header records
    summaries = filter(lambda x: x != ['url', 'summary'], summaries)
    logging.info('--------------------- done reading data, number of summaries: {}'.format(len(summaries)))
    summaries = summaries[:10]  # short for example
    t1 = time()
    classify_wrapper(summaries, output_filename)
    t2 = time()
    logging.info('classifying {} summaries took: {} seconds'.format(len(summaries), round(t2 - t1, 2)))