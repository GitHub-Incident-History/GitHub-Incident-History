import requests
import json
import os
from tqdm import tqdm
import sys

def download_all_incident_codes():
    incident_codes = []
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    for page in tqdm(range(1, 52)):
        url = f'https://www.githubstatus.com/history?page={page}'
        print(url)
        response = requests.get(url, headers=headers)
        months = response.json()['months']
        for month in months:
            incidents = month['incidents']
            for incident in incidents:
                # {
                #     'code': '8tnqgcg1qkk1',
                #     'name': 'Incident with Actions, API Requests, Pages and Pull Requests',
                #     'message': 'This incident has been resolved.',
                #     'impact': 'minor',
                #     'timestamp': "Aug <var data-var='date'>10</var>, <var data-var='time'>00:17</var> - <var data-var='time'>01:30</var> UTC"
                # }
                # Exclude all maintenances
                # Only include resolved incidents
                if incident['impact'] != 'maintenance' and incident['status'] == 'resolved':
                    incident_codes.append(incident['code'])
    with open('incident_codes.json', 'w') as file:
        json.dump(incident_codes, file)


def read_incident_codes():
    incident_codes = []
    with open('incident_codes.json', 'r') as file:
        incident_codes = json.load(file)
    return incident_codes


def get_incident(id: str):
    url = f'https://www.githubstatus.com/api/v2/incidents/{id}.json'
    response = requests.get(url)
    return response.json()

def download_incident_record(id: str):
    incident = get_incident(id)
    with open(f'incidents/{id}.json', 'w') as file:
        json.dump(incident, file, indent=4)

def download_all_incident_records():
    incident_codes = read_incident_codes()
    for incident_code in tqdm(incident_codes):
        download_incident_record(incident_code)


def read_incident(id: str):
    with open(f'incidents/{id}.json', 'r') as file:
        incident = json.load(file)
    return incident

def read_all_incidents():
    incident_codes = read_incident_codes()
    incidents = []
    for incident_code in incident_codes:
        incidents.append(read_incident(incident_code))
    return incidents

# check whether the incident_updates is in the new format
# the new format splits updates into different dictionaries
# while the old format compose everything in the body
def is_new_version(incident):
    date = incident['incident']['created_at']
    # incidents/396z7tmkc5nh.json is the first incident adopting the new format
    return date >= '2019-01-02T16:32:49.277Z'


def parse_body(incident):
    body = ''
    incident_updates = incident['incident']['incident_updates']
    if is_new_version(incident):
        incident_updates.reverse()
        for update in incident_updates:
            body += update['created_at']
            body += ' - '
            body += update['status']
            body += ': '
            body += update['body']
            body += '\n'
    else:
        assert len(incident_updates) == 1
        raw: str = incident_updates[0]['body']
        # remove <ul> </ul>
        raw = raw.removeprefix('<ul>')
        raw = raw.removesuffix('</ul>')
        raw_updates = raw.split('<li>')
        for raw_update in raw_updates:
            if len(raw_update) > 0:
                raw_update = raw_update.removeprefix('<strong>')
                raw_update = raw_update.removesuffix('</li>')
                update = raw_update.split('</strong>')
                body += update[0] + update[1]
                body += '\n'
    return body

def create_git_commit_message(title, body):
    file_name = 'commit_message.txt'
    with open(file_name, 'w') as file:
        file.write(title)
        file.write('\n\n')
        file.write(body)
    return file_name

def create_incident_commits():
    incidents = read_all_incidents()
    incidents.sort(key=lambda x: x['incident']['created_at'])
    for incident in tqdm(incidents):
        date = incident['incident']['created_at']
        name = incident['incident']['name']
        body = parse_body(incident)
        filename = create_git_commit_message(name, body)
        cmd = f'git commit --allow-empty -F "{filename}"'
        os.environ['GIT_AUTHOR_DATE'] = date
        os.environ['GIT_COMMITTER_DATE'] = date
        os.system(cmd)
        # break

def get_recent_incidents():
    return requests.get('https://www.githubstatus.com/api/v2/incidents.json').json()['incidents']

def main():
    # incident_codes = read_incident_codes()
    # print(len(incident_codes))
    # download_all_incident_codes()
    # download_all_incident_records()
    create_incident_commits()

def print_help():
    print("Usage: python main.py [options]")
    print("Options")
    print("update               Update incident data")
    print("commit               Update github-incident-history commit history")

def update_data():
    incident_codes = read_incident_codes()
    recent_incidents = get_recent_incidents()
    recent_incidents.reverse()
    for incident in recent_incidents:
        if (incident['id'] not in incident_codes) and (incident['status'] == 'resolved') and (incident['impact'] != 'maintenance'): 
            incident_codes.insert(0, incident['id'])

    with open('incident_codes.json', 'w') as file:
        json.dump(incident_codes, file)

    for incident_code in incident_codes:
        file_name = f'incidents/{incident_code}.json'
        if os.path.exists(file_name) == False:
            download_incident_record(incident_code)

def get_the_latest_incident():
    incidents = read_all_incidents()
    incident = max(incidents, key=lambda x: x['incident']['created_at'])
    return incident

def render(filename, **kwargs):
    s = ""
    with open(filename, 'r') as file:
        s = file.read()
    for key, value in kwargs.items():
        s = s.replace("{{ " + key + " }}", value).strip(' \n')
    with open(filename, 'w') as file:
        file.write(s)

def render_README():
    latest_incident = get_the_latest_incident()
    details = parse_body(latest_incident)
    render("README.md", latest_incident_details=details)

def update_commits():
    os.system('git config user.email 100416422+GitHub-Incidents-History@users.noreply.github.com')
    os.system('git config user.name GitHub-Incidents-History')    
    os.system('git branch -D github-incidents-history')
    os.system('git checkout --orphan github-incidents-history')
    os.system('git reset')
    os.system('git add .github/workflows/update_data.yml')

    render_README()
    os.system('git add README.md')
    os.system('git add stats.svg')
    os.system('git add streak.svg')
    os.system('git add top.svg')

    create_incident_commits()
    os.system('git push -u origin github-incidents-history -f')

if __name__ == '__main__':
    render_README()
    if len(sys.argv) != 2:
        print_help()
        exit(1)
    command = sys.argv[1]
    if command == 'update':
        update_data()
    elif command == 'commit':
        update_commits()
    else:
        print_help()
        exit(1)
