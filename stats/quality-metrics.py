# -*- coding: utf-8 -*-

import requests
import collections
import urllib 
from bs4 import BeautifulSoup


def get_values(url, is_old):
	page = urllib.urlopen(url)
	strpage = page.read().decode('utf-8')
	soup = BeautifulSoup(strpage, "html.parser")
	records = soup.find_all("div", "infoscience_record")
	contents = []
	for record in records:
		if is_old:
			tag = record.find("span", "infoscience_title")
			if tag:
				content = tag.text.strip()
			else:
				content = record.find("h3", "infoscience_title").text.strip()
		else:
			tag = record.find("span", "infoscience_my_title")
			if tag:
				content = tag.text.strip()
			else:
				content = record.find("h3", "infoscience_title").text.strip()
		content = content.strip('. ')
		contents.append(content)
	return contents
	

file_urls = open('data/infoscience_exports_all_new_url.csv', 'r') 
data = file_urls.readlines()[1:]

urls = []
for line in data: 
	values = line.split(',')
	url = {}
	url['legacy'] = values[0]
	url['old'] = values[1]
	url['new'] = values[2]
	url['parameters'] = values[3]
	url['new_url_in'] = values[4]
	urls.append(url)

file_urls.close()


file_updated = open('data/need_update_2018.04.25.csv', 'r') 
data = file_updated.readlines()[1:]

records_added_id = []
records_added_counter = []
for line in data: 
	values = line.split(',')
	record = {}
	records_added_id.append(int(values[0]))
	records_added_counter.append(values[4])

file_updated.close()



results = []
for counter, url in enumerate(urls):
	print(counter+1)
	title_old = get_values(url['old'], True)
	title_new = get_values(url['new'], False)
	#print [item for item, count in collections.Counter(title_old).items() if count > 1]
	set_old = set(title_old)
	set_new = set(title_new)
	result = {}
	result['legacy'] = url['legacy']
	result['new_url_in'] = url['new_url_in']
	result['parameters'] = url['parameters']
	result['nb_titles_old'] = len(title_old)
	result['nb_titles_new'] = len(title_new)
	result['nb_set_old'] = len(set_old)
	result['nb_set_new'] = len(set_new)
	result['intersect'] = len(set_old.intersection(set_new))
	result['diff_old_new'] = len(set_old.difference(set_new))
	result['diff_new_old'] = len(set_new.difference(set_old))
	if int(url['legacy']) not in records_added_id:
		result['updated'] = "--"
	else:
		result['updated'] = records_added_counter[records_added_id.index(int(url['legacy']))]
	results.append(result)



file_results = open('results.csv', 'w')

file_results.write('legacy_id,number_titles_old,number_titles_new,number_set_old,number_set_new,intersect,old-new,new-old,updated,old_key,generated_url' + '\n') 

file_results.write('=========================\n')
file_results.write('SEEMS OK\n')

for result in results:
	if result['intersect'] == result['nb_set_old']:
		line = str(result['legacy'])
		line += "," + str(result['nb_titles_old'])
		line += "," + str(result['nb_titles_new'])
		line += "," + str(result['nb_set_old'])
		line += "," + str(result['nb_set_new'])
		line += "," + str(result['intersect'])
		line += "," + str(result['diff_old_new'])
		line += "," + str(result['diff_new_old'])
		line += "," + result['updated']
		line += "," + result['parameters']
		line += "," + result['new_url_in']
		file_results.write(line + '\n')

file_results.write('\n')
file_results.write('=========================\n')
file_results.write('PROBLEMS\n')

for result in results:
	if result['intersect'] != result['nb_set_old']:
		line = str(result['legacy'])
		line += "," + str(result['nb_titles_old'])
		line += "," + str(result['nb_titles_new'])
		line += "," + str(result['nb_set_old'])
		line += "," + str(result['nb_set_new'])
		line += "," + str(result['intersect'])
		line += "," + str(result['diff_old_new'])
		line += "," + str(result['diff_new_old'])
		line += "," + result['updated']
		line += "," + result['parameters']
		line += "," + result['new_url_in']
		file_results.write(line + '\n')

	
file_results.close()
