###Creating a dictionary to insert into hierarchy###
def create_temp_dict (project):
	temp_dict = {}
	temp_dict ['id'] = project.get('id')
	temp_dict ['name'] = project.get('name')
	return temp_dict
########################################################

###Recursive method to retrieve the project ID to map to###
def get_project_id (dictionary, search_key, search_value):
	def get_occurrence (dictionary, search_key, search_value, level=[], key_if_list=[], counter_if_list=[]) :
		project_id = None
		keys = list(dictionary.keys())
		for key in keys:
			if search_key == key:
				if (dictionary.get (search_key) == search_value):
					for j in range (len(key_if_list)):
						level.append (key_if_list[j])
						level.append (counter_if_list[j])
					key_if_list = []
					counter_if_list = []
					project_id = dictionary.get (search_key)
					break

			if project_id is None:
				values = dictionary[key]
				if isinstance(values, dict):
					value = values
					level.append (key)
					project_id, level = get_occurrence (value, search_key, search_value, level)

			if project_id is None:
				if isinstance(values, list):
					for i in range (len(values)):
						if project_id is None:
							value = values[i]
							if isinstance (value, dict):
								if key_if_list:
									move_to_next_item = 0
									for counter, key_value in enumerate(key_if_list):
										if key == key_value:
											key_if_list[counter] = key
											counter_if_list[counter] = str(i)
											del key_if_list[counter+1:]
											del counter_if_list[counter+1:]
											move_to_next_item=1
									if move_to_next_item == 0:
										key_if_list.append (key)
										counter_if_list.append (str(i))	
								else:
									key_if_list.append (key)
									counter_if_list.append (str(i))
								project_id, level = get_occurrence (value, search_key, search_value, level, key_if_list, counter_if_list)
		return project_id, level
	return get_occurrence (dictionary, search_key, search_value)
########################################################

###Assigning the sub-projects along with their workbooks###
def assign_non_parent_projects (project, projects_with_workbooks, all_projects, hierarchy):
	id_in_hierarchy, nests = get_project_id(hierarchy, 'id', project.get('parentProjectId'))
	if id_in_hierarchy:
		nest ='.'.join(nests)  
		temp_dict = create_temp_dict (project)
		if isinstance (projects_with_workbooks.get(project.get('id'), projects_with_workbooks), list):
			temp_dict ['workbooks'] = projects_with_workbooks.get(project.get('id'), projects_with_workbooks)
			projects_with_workbooks.pop(project.get('id'))

		if (nest.rfind('subprojects')) == -1:
			subproject_count = 'subprojects0'
		else:
			subproject_count = 'subprojects{count}' .format(count=str(int(nest[nest.rfind('subprojects')+11])+1))
		try:
			if hierarchy[nest][subproject_count][0]:
				hierarchy[nest][subproject_count].append(temp_dict) 
		except:
			temp_subproject = []
			temp_subproject.append(temp_dict)
			hierarchy[nest][subproject_count] = temp_subproject						
	else:	
		try:
			for proj in all_projects:
				if proj.get('id') == project.get('parentProjectId'):
					project = proj
					assign_non_parent_projects (project, projects_with_workbooks, all_projects, hierarchy)
		except:
			pass
########################################################