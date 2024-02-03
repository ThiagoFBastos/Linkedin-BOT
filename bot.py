#!/usr/bin/env python3

import sys
from linkedin import Linkedin
from pandas import DataFrame
import json

PARAMS = 'input/params.json' if sys.argv[-1] != 'LOCAL' else 'input/fake_params.json'

def main():
    with open(PARAMS, 'r') as fp:
        params = json.load(fp)

        username = params.get('username')
        params.pop('username')

        password = params.get('password')
        params.pop('password')

        output = params.get('output')
        params.pop('output')

        cutoff = params.get('cutoff')
        params.pop('cutoff')

        search = params.get('search')
        params.pop('search')

        api = Linkedin(username = username, password = password, cutoff = cutoff, search = search)

        jobs = api.search_jobs(**params)

        if len(jobs):
            jobs_df = DataFrame(jobs.values())
            jobs_df = jobs_df.sort_values(by = ['score'], ascending = False)
            jobs_df.to_csv(f'output/{output}.csv', index = False)
 
if __name__ == '__main__':
    main()
