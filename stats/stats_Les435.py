


file_legacy = open('data/legacy.txt', 'r')
legacies = []
export = {}
for line in file_legacy: 
	if "------" in line:
		if 'id' not in export:
			export['id'] = -1
		if 'pattern' not in export:
			export['pattern'] = ""
		if 'collection' not in export:
			export['collection'] = ""
		if 'restriction' not in export:
			export['restriction'] = ""
		if 'filters' not in export:
			export['filters'] = []
		if 'basket_id' not in export:
			export['basket_id'] = ""	
		legacies.append(export)
		export = {}
	if "legacy id " in line:
		export['id'] = int(line.replace("legacy id ", ""))
	elif "search_pattern : " in line:
		export['pattern'] = line.replace("search_pattern : ", "")
	elif "search_collection : " in line:
		export['collection'] = line.replace("search_collection : ", "")
	elif "search_field_restriction : " in line:
		export['restriction'] = line.replace("search_field_restriction : ", "")
	elif "search_filter : " in line:
		export['filters'] = line.replace("search_filter : ", "").split(",")
	elif "search_basket_id " in line:
		export['basket_id'] = int(line.replace("search_basket_id : ", ""))

file_legacy.close()



file_index_migrated = open('results/ids_to_migrate.txt', 'r')
migrated = []
for line in file_index_migrated: 
	migrated.append(int(line))
file_index_migrated.close()




file_Les435 = open('data/Les435.txt', 'r')
ids = []
Les435_curator = 0
for line in file_Les435: 
	Les435_curator += 1
	ids.append(int(line))
file_Les435.close()



filters = {}
records = []
counter = 0

for id_ in ids:
	record = {}
	record['id'] = id_
	record['is_migrated'] = id_ in migrated
	if record['is_migrated']:
		counter += 1	
	for legacy in legacies:
		if legacy['id'] == id_:
			if legacy['basket_id']:
				record['group'] = 'basket'
			elif legacy['pattern']:
				if legacy['collection']:
					if legacy['restriction']:
						if legacy['filters']:
							record['group'] = 'pattern_collection_restriction_filters'
						else:
							record['group'] = 'pattern_collection_restriction'
					else:
						if legacy['filters']:
							record['group'] = 'pattern_collection_filters'
						else:
							record['group'] = 'pattern_collection'
				else:
					if legacy['restriction']:
						if legacy['filters']:
							record['group'] = 'pattern_restriction_filters'
						else:
							record['group'] = 'pattern_restriction'
					else:
						if legacy['filters']:
							record['group'] = 'pattern_filters'
						else:
							record['group'] = 'pattern'
			else:
				if legacy['collection']:
					if legacy['restriction']:
						if legacy['filters']:
							record['group'] = 'collection_restriction_filters'
						else:
							record['group'] = 'collection_restriction'
					else:
						if legacy['filters']:
							record['group'] = 'collection_filters'
						else:
							record['group'] = 'collection'
				else:
					if legacy['restriction']:
						if legacy['filters']:
							record['group'] = 'restriction_filters'
						else:
							record['group'] = 'restriction'
					else:
						if legacy['filters']:
							record['group'] = 'filters'
						else:
							record['group'] = 'none'
	records.append(record)




file_results = open('results/stats_Les435_results.csv', 'w')
file_results.write("id,group,is_migrated\n")
for record in records:
	file_results.write(str(record['id']) + "," + str(record['group']) + "," + str(record['is_migrated']) + "\n")
file_results.close()

					
		
