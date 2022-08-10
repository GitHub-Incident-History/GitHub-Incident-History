import requests
import json
from tqdm import tqdm


def download_all_incident_codes():
    incident_codes = []
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    for page in range(1, 52):
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

def main():
    # incident_codes = read_incident_codes()
    # print(len(incident_codes))
    # download_all_incident_codes()
    download_all_incident_records()


if __name__ == '__main__':
    main()
