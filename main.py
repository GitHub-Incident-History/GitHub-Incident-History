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


def create_incident_commits():
    incident_codes = read_incident_codes()
    incidents = []
    for incident_code in incident_codes:
        incidents.append(read_incident(incident_code))
    incidents.sort(key=lambda x:x['incident']['created_at'])
    for incident in tqdm(incidents):
        date = incident['incident']['created_at']
        name = incident['incident']['name']
        cmd = f'git commit --allow-empty -m "{name}"'
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
