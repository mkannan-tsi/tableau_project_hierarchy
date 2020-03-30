# tableau_project_hierarchy
Creating a hierarchy of all the projects within a site that contain workbooks that a user has access to. Useful for displaying the same content structure in an embedded portal that is displayed when a user logs into Tableau Server/ Tableau Online.

The result is a JSON output that can be parsed for display.

Some notes -
* Script written for Python 3.7
* Please ensure that pre-requisites -
  * pip install requests
  * pip install dotty_dict
* Fill in the following details in hierarchy.py -
  * server_name (server IP with http:// or https://)
  * site_url_id (site name)
  * personal access token details or username/ password (depending on how you wish to login)
  * username that you want to search for (you can search for workbooks that a specific user has access to. If you'd like to do a general search then you can enter the admin's username instead)

Run the script by running 'python hierarchy.py)  
