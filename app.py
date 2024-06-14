#!/usr/local/bin/python3
from flask import Flask, render_template, jsonify, request
from urllib.request import Request, urlopen
from urllib import parse
import json, urllib.error, os

private_token = os.environ['TOKEN']
gitlab_server = os.environ['SERVER']

app = Flask(__name__)

@app.route('/')
def root():
    return render_template('index.html')


@app.route('/mr')
def get_merge_requests():
    year = request.args.get('year')
    req = Request('http://' + gitlab_server + '/api/v4/merge_requests')
    req.add_header('PRIVATE-TOKEN', private_token)
    resp = urlopen(req)
    content = json.loads(resp.read())
    data = [x for x in content if year in x['created_at']]
    return jsonify(data)


@app.route('/issues')
def get_issues():
    year = request.args.get('year')
    req = Request('http://' + gitlab_server + '/api/v4/issues')
    req.add_header('PRIVATE-TOKEN', private_token)
    resp = urlopen(req)
    content = json.loads(resp.read())
    data = [x for x in content if year in x['created_at']]
    return jsonify(data)


@app.route('/grant')
def get_args():
    username = request.args.get('user')
    group = request.args.get('group')
    repo = request.args.get('repo')
    role = request.args.get('role')

    if role == "Guest":
        role = 10
    elif role == "Reporter":
        role = 20
    elif role == "Developer":
        role = 30
    elif role == "Maintainer":
        role = 40
    elif role == "Owner":
        role = 50

    args = {"username": username, "group": group, "repo": repo, "role": role}

    #return jsonify(data)
    if group is None:
        try:
            out = add_to_project(username, repo, role)
        except:
            return "Wrong args! "+str(args)
    else:
        try:
            out = add_to_group(username, group, role)
        except:
            return "Wrong args! "+str(args)

    return out

def get_user_id(username):
    req = Request('http://'+gitlab_server+'/api/v4/users')
    req.add_header('PRIVATE-TOKEN', private_token)
    resp = urlopen(req)
    content = resp.read()
    users = json.loads(content)
    data = [x for x in users if x['username'] in username]
    return (data[0]['id'])


def get_group_id(group_name):
    req = Request('http://'+gitlab_server+'/api/v4/groups')
    req.add_header('PRIVATE-TOKEN', private_token)
    resp = urlopen(req)
    content = resp.read()
    groups = json.loads(content)
    data = [x for x in groups if x['name'] in group_name]
    return (data[0]['id'])


def get_project_id(project_name):
    req = Request('http://'+gitlab_server+'/api/v4/projects')
    req.add_header('PRIVATE-TOKEN', private_token)
    resp = urlopen(req)
    content = resp.read()
    projects = json.loads(content)
    data = [x for x in projects if x['name'] in project_name]
    return (data[0]['id'])


def check_group_membership(username, group_name):
    group_id = str(get_group_id(group_name))
    req = Request('http://'+gitlab_server+'/api/v4/groups/'+group_id+'/members')
    req.add_header('PRIVATE-TOKEN', private_token)
    resp = urlopen(req)
    content = json.loads(resp.read())
    data = [x for x in content if x['username'] == username ]
    if len(data) == 0:
        return False
    else:
        return True


def check_project_membership(username, project_name):
    project_id = str(get_project_id(project_name))
    req = Request('http://'+gitlab_server+'/api/v4/projects/'+project_id+'/members')
    req.add_header('PRIVATE-TOKEN', private_token)
    resp = urlopen(req)
    content = json.loads(resp.read())
    data = [x for x in content if x['username'] == username ]
    if len(data) == 0:
        return False
    else:
        return True


def add_to_group(username, group_name, role):
    user_id = str(get_user_id(username))
    group_id = str(get_group_id(group_name))
    if check_group_membership(username, group_name) == False:
        data = parse.urlencode({"user_id":user_id,"access_level":str(role)}).encode()
        req = Request('http://' + gitlab_server + '/api/v4/groups/' + group_id + '/members', data=data)
    else:
        req = Request('http://' + gitlab_server + '/api/v4/groups/' + group_id + '/members/'+user_id+'?access_level='+str(role), method='PUT')

    try:
        req.add_header('PRIVATE-TOKEN', private_token)
        resp = urlopen(req)
        content = json.loads(resp.read())
        return jsonify(content)
    except urllib.error.HTTPError as err:
        error = json.loads(err.read())
        return jsonify(error)

def add_to_project(username, project_name, role):
    user_id = str(get_user_id(username))
    project_id = str(get_project_id(project_name))
    print(check_project_membership(username, project_name))
    if check_project_membership(username, project_name) == False:
        data = parse.urlencode({"user_id": user_id,"access_level": str(role)}).encode()
        req = Request('http://' + gitlab_server + '/api/v4/projects/' + project_id + '/members', data=data)
    else:
        req = Request('http://' + gitlab_server + '/api/v4/projects/' + project_id + '/members/'+user_id+'?access_level='+str(role), method='PUT')

    try:
        req.add_header('PRIVATE-TOKEN', private_token)
        resp = urlopen(req)
        content = json.loads(resp.read())
        return jsonify(content)
    except urllib.error.HTTPError as err:
        error = json.loads(err.read())
        return jsonify(error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
  
