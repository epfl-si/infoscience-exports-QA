# -*- coding: utf-8 -*-

import requests
import collections
import urllib
import csv
from bs4 import BeautifulSoup
import hashlib
from fcache.cache import FileCache


mycache = FileCache('infoscience_urlopen', flag='cs', app_cache_dir='.')

def get_values(url, is_old, can_cache):
	cache_name = hashlib.sha1(url).hexdigest()
	if can_cache and mycache.get(cache_name):
		strpage = mycache[cache_name]
	else:
		page = urllib.urlopen(url, context=context)
		strpage = page.read().decode('utf-8')
		if can_cache:
			mycache[cache_name] = strpage
	soup = BeautifulSoup(strpage, "html.parser")
	records = soup.find_all("a", "infoscience_link_detailed")
	contents = []
	if not records:
		if is_old:
			records = soup.find_all("div", "readable_link")
			for record in records:
				texts = record.text.strip()
				if "Detailed record" in texts or u"Notice détaillée" in texts:
					texts = texts.split()
					for text in texts:
						if "http" in text:
							tags = text.split('/')
							content = int(tags[4].replace("?ln=fr", "").replace("?ln=en", "").replace("?ln=de", ""))
							contents.append(content)
		else:
			records = soup.find_all("p", "infoscience_links")
			for record in records:
				texts = record.text.strip().split()
				for text in texts:
					if "idevelopsrv25" in text:
						tags = text.split('/')
						content = int(tags[4].replace("?ln=fr", "").replace("?ln=en", "").replace("?ln=de", ""))
						contents.append(content)
	else:
		for record in records:
			tags = record['href'].split('/')
			content = int(tags[4].replace("?ln=fr", "").replace("?ln=en", "").replace("?ln=de", ""))
			contents.append(content)
	return contents


def get_line(result):
	line = str(result['legacy'])
	line += "," + str(result['nb_set_old'])
	line += "," + str(result['nb_set_new'])
	line += "," + str(result['intersect'])
	line += "," + str(result['diff_old_new'])
	line += "," + str(result['diff_new_old'])
	line += "," + str(result['updated'])
	line += "," + result['parameters']
	line += "," + result['new_url_in']
	return line



reader = csv.DictReader(open('data/infoscience_exports_all_new_url.csv', 'r'))
urls = []
for row in reader:
	url = {}
	url['legacy'] = row['legacy_id']
	url['old'] = row['old_url']
	url['new'] = row['new_url']
	url['parameters'] = row['old_key']
	url['new_url_in'] = row['generated_url']
	urls.append(url)



file_updated = csv.DictReader(open('data/need_update_2018.04.30.csv', 'r'))
records_added_id = []
records_added_counter = []
for line in file_updated: 
	record = {}
	records_added_id.append(int(line['legacy id']))
	records_added_counter.append(line['number of new elements since migration'])



results = []
for counter, url in enumerate(urls):
	print(counter+1)
	contents_old = get_values(url['old'], True, True)
	contents_new = get_values(url['new'], False, False)
	#print [item for item, count in collections.Counter(contents_old).items() if count > 1]
	set_old = set(contents_old)
	set_new = set(contents_new)
	result = {}
	result['legacy'] = url['legacy']
	result['new_url_in'] = url['new_url_in']
	result['parameters'] = url['parameters']
	result['nb_set_old'] = len(set_old)
	result['nb_set_new'] = len(set_new)
	result['intersect'] = len(set_old.intersection(set_new))
	result['diff_old_new'] = len(set_old.difference(set_new))
	result['diff_new_old'] = len(set_new.difference(set_old))
	#print(str(set_old.difference(set_new)))
	#print(str(set_new.difference(set_old)))
	if int(url['legacy']) not in records_added_id:
		result['updated'] = "--"
	else:
		result['updated'] = int(records_added_counter[records_added_id.index(int(url['legacy']))])
	results.append(result)


results_ok = []
results_maybe = []
results_nok = []
for result in results:
	if result['intersect'] == result['nb_set_old'] and result['diff_new_old'] == result['updated']:
		results_ok.append(result)
	elif result['intersect'] == result['nb_set_old'] and result['intersect'] == result['nb_set_new']:
		results_ok.append(result)
	elif result['intersect'] + result['updated'] == result['nb_set_new']:
		results_ok.append(result)
	elif result['intersect'] == result['nb_set_old'] and result['intersect'] >= 10:
		results_maybe.append(result)
	else:
		results_nok.append(result)


file_results = open('results/quality_metrics_results.csv', 'w')

file_results.write('legacy_id,number_set_old,number_set_new,intersect,old-new,new-old,updated,old_key,generated_url' + '\n') 

file_results.write('=========================\n')
file_results.write('OK\n')

for result in results_ok:
	line = get_line(result)
	file_results.write(line + '\n')

file_results.write('\n')
file_results.write('=========================\n')
file_results.write('MAYBE\n')

for result in results_maybe:
	line = get_line(result)
	file_results.write(line + '\n')

file_results.write('\n')
file_results.write('=========================\n')
file_results.write('PROBLEMS\n')

for result in results_nok:
	line = get_line(result)
	file_results.write(line + '\n')
	
file_results.close()


file_seems_to_be_ok_to_migrate = open('results/ids_to_migrate.txt', 'w')

for result in results_ok:
	file_seems_to_be_ok_to_migrate.write(str(result['legacy']) + '\n')

file_seems_to_be_ok_to_migrate.close()
