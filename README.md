# finsmes-ner
Use Named Entity Recognition with FINSMES Articles. See http://www.finsmes.com/

# Environment Installation
`$ pip install requirements.txt` in a virtual environment to get the complete list of requirements. 

# Stanford NER Installation
1. Download the Stanford Named Entity Recognizer zip file: 

https://nlp.stanford.edu/software/CRF-NER.html#Download

2. With the current code, the key files in the zip file are `stanford-ner.jar` and `english.muc.7class.distsim.crf.ser.gz`. Update the paths for `MODEL_7_CLASSES_PATH` and `NER_JAR_PATH` in `finsmes_ner.py`.
https://github.com/ngreenwald89/finsmes-ner/blob/master/finsmes_ner.py

# Getting the FINSMES files via Scrapy
`$ cd finsmes`

`$ scrapy crawl finsmes`

Should take about 5 minutes to run. 
See https://doc.scrapy.org/en/latest/intro/tutorial.html and example scraped page: http://www.finsmes.com/category/usa/page/2.

Right now just getting article summaries, rather than entire articles. Right now hardcoded to get 1816 pages, likely to be more over time.

# Generating Named Entity files
After setting up environment, installing Stanford NER, and getting FINSMES files via Scrapy, can run `finsmes_ner.py` to create output csv file with Named Entities extracted for the summaries. Note that it takes ~1-2 seconds per summary, so can take hours to run for all articles if running with just 1 or 2 processors. Update code under `if __name__ == '__main__'` as needed, in particular `FINSMES_FILE_PATH_PATTERN`



