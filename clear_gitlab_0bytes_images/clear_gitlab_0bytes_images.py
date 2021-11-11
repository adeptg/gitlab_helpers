#!/usr/bin/env python3

#ToDo: better exception handling in  repository.tags.get(id=tag.name). Need to add to the list only on HTTP 404

import requests
import os
import gitlab
import sys
import time

gitlab_instance = input("Please specify gitlab hostname (without leading http): ")
project_name = input("Please specify project name with the namespace if any (example: test/test): ")
access_token = input("please specify access token for this project. It needs delete tag priviledge: ")

gl = gitlab.Gitlab("https://"+gitlab_instance, private_token=access_token)

project = gl.projects.get(project_name)

repositories = project.repositories.list()

for repository in repositories:    
    broken_tags = []
    print("found repository: " + repository.name)
    tags = repository.tags.list(all=True)
    for tag in tags:        
        try:
            repository.tags.get(id=tag.name)        
        except:            
            print("adding to a broken list: " + tag.name)
            broken_tags.append(tag.name)
    print("%s repository has %s broken tags" % (repository.name, len(broken_tags)))
    if broken_tags:
        runcommand = ' && '.join(["sudo docker build -t "+gitlab_instance+":4567/"+project_name+"/"+repository.name+":"+broken_tag+" . && sudo docker push "+gitlab_instance+":4567/"+project_name+"/"+repository.name+":"+broken_tag for broken_tag in broken_tags])
        print(runcommand)
        input("press ENTER when done")
        for broken_tag in broken_tags:
            tag = repository.tags.get(id=broken_tag)
            print("Deleting tag: " + broken_tag)
            tag.delete()
            time.sleep(60)
