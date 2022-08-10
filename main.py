import requests
import json
import os
from tqdm import tqdm


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
                if (incident['impact'] != 'maintenance'):
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
    #
    response = requests.get(url)
    return response.json()


def download_all_incident_records():
    incident_codes = read_incident_codes()
    for incident_code in tqdm(incident_codes):
        # print(incident_code)
        incident = get_incident(incident_code)
        with open(f'incidents/{incident_code}.json', 'w') as file:
            json.dump(incident, file, indent=4)


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


def main():
    # incident_codes = read_incident_codes()
    # print(len(incident_codes))
    # download_all_incident_codes()
    # download_all_incident_records()
    create_incident_commits()


if __name__ == '__main__':
    main()
