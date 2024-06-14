### Gitlab tool
---

#### Build docker:
```sh
docker buikd -t gitlab-tool .
```

#### Run docker container:
```sh
docker run --name gitlab-tool -p 80:5000 -e TOKEN="<api token>" -e SERVER="<gitlab server>" gitlab-tool:latest
```

#### Usage:
---
Point your browser to http://127.0.01 to get help page

##### Grant user group or repository permissions:

Where [role string] is one of: [Guest, Reporter, Developer, Maintainer, Owner]  

``
/grant?user=[username]&role=[role string]&group=[group name]  
  ``

``
/grant?user=[username]&role=[role string]&repo=[repository name]
``
  

##### List issues/merge requests created on the given year:

``
/issues?year=YYYY  
``
``
/mr?year=YYYY
``
