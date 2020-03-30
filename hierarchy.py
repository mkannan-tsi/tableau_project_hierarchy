import requests, json
from dotty_dict import dotty
from ProjectMethods import *

###Important details to fill in###
server_name = ""   
version = ""     
site_url_id = ""
personal_access_or_username = 1 #set to 1 if personal access tokens are to be used
personal_access_token_name = ""         
personal_access_token_secret = ""
admin_username = ""
admin_password = ""
username_to_search_for = ""
########################################################

###Signing In####
payload_personal_access = 	{
				"credentials": 
				{ 
					"personalAccessTokenName": personal_access_token_name, 
				  	"personalAccessTokenSecret": personal_access_token_secret, 
				  	"site": {"contentUrl": site_url_id }
				}
			}
payload_username_password = 	{
				"credentials": 
				{ 
					"name": admin_username, 
				  	"password": admin_password, 
				  	"site": {"contentUrl": site_url_id }
				}
			}

if personal_access_or_username == 1:
	payload = payload_personal_access
	version = "3.6"
else:
	payload = payload_username_password
	version = "3.0"

signin_url = "{server}/api/{version}/auth/signin".format(server=server_name, version=version)
headers = 	{
				'accept': 'application/json',
				'content-type': 'application/json'
			}

try:
	r = requests.post(signin_url, json=payload, headers=headers, verify=False)
	response = json.loads(r.content)
	token = response["credentials"]["token"]
	site_id = response["credentials"]["site"]["id"]
except:
	print ("Error signing In")
########################################################

###Requesting the specific user's LUID###
try:
	users_url = "{server}/api/{version}/sites/{site_id}/users?filter=name:eq:{user_name}".format(server=server_name, version=version, site_id=site_id, user_name=username_to_search_for)
	headers['X-tableau-auth'] = token
	r = requests.get (users_url, headers=headers)
	response = json.loads(r.content)
	user_id =  response["users"]["user"][0]["id"]
except:
	print ("Error retrieving user ID to search for")
########################################################

###Requesting the accessible workbooks###
try:
	workbooks_url = u"{server}/api/{version}/sites/{site_id}/users/{user_id}/workbooks?pageSize=1000".format(server=server_name, version=version, site_id=site_id, user_id=user_id)
	r = requests.get (workbooks_url, headers=headers)
	response = json.loads(r.content)
	projects_with_workbooks = {}
	for workbook in response["workbooks"]['workbook']:
		if projects_with_workbooks.get (workbook["project"]["id"]) is None:
			projects_with_workbooks[workbook["project"]["id"]] = [workbook["name"]]
		else:
			projects_with_workbooks[workbook["project"]["id"]].append (workbook['name'])
except:
	print ("Error retrieving workbooks with correct permissions")
########################################################

###Requesting the details of all projects###
try:
	projects_url = '{server}/api/{version}/sites/{site_id}/projects?_fields_=all&pageSize=500'.format(server=server_name, version=version, site_id=site_id)
	r = requests.get (projects_url, headers=headers)
	response = json.loads(r.content)
	all_projects = response["projects"]["project"]
except:
	print ("Error retrieving all projects")
hierarchy = {
				"projects" : {
								"project" : []
							 }
			}
hierarchy = dotty (hierarchy)
########################################################

###Adding top-level projects###
try:
	for project in all_projects:
		if project.get('parentProjectId') is None:
			temp_dict = create_temp_dict(project)
			hierarchy['projects']['project'].append (temp_dict)
except:
	print ("Error adding top-level projects")
########################################################

###Adding workbooks for top-level projects###
try:
	for project_id in list(projects_with_workbooks.keys()):
		id_in_hierarchy, nests = get_project_id(hierarchy, 'id', project_id)
		if id_in_hierarchy:
			nest ='.'.join(nests) 
			hierarchy[nest]['workbooks'] = projects_with_workbooks.get(project_id, projects_with_workbooks)
			projects_with_workbooks.pop(project_id)
except:
	print ("Error adding workbooks for top-level projects")
########################################################

###Adding sub-projects with their workbooks###
try:
	while len(list(projects_with_workbooks.keys())) > 0:
		for project_id in list(projects_with_workbooks.keys()):
			for project in all_projects:
				if project.get('id') == project_id:
					assign_non_parent_projects (project, projects_with_workbooks, all_projects, hierarchy)
except:
	print ("Error assigning sub-projects and their workbooks")
########################################################

###Removing top-level projects that have no workbooks###
remove_project_list = []
for project in hierarchy['projects']['project']:
	if ('workbooks' not in list(project.keys())) and ('subprojects0' not in list(project.keys())):
		remove_project_list.append (project)
for project in remove_project_list:
	hierarchy['projects']['project'].remove(project)
########################################################

print (hierarchy)