import gzip
import os
import requests
from faceit_get_funcs import match_details, player_details


def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        # r.raise_for_status()
        if r.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)
        else:
            print(r.status_code)
            return None
    return local_filename


def unpack_gz(local_filename):
    if local_filename is None:
        print('nothing to unpack')
    elif local_filename.endswith('.gz'):
        inF = gzip.open(local_filename, 'rb')
        outF = open(local_filename.replace('.gz', ''), 'wb')
        outF.write(inF.read())
        inF.close()
        outF.close()

        # Delete gzip file
        os.remove(local_filename)
        print(f'{local_filename} unpacked and deleted')
    else:
        print('nothing to unpack')


def get_demos_from_match(match_id):
    # for demourl in match_details('1-3ae5df7f-cb2e-467b-bbd1-6d8aa280728e')['demo_url']:
    if 'demo_url' in match_details(match_id):
        for demourl in match_details(match_id)['demo_url']:
            filename = download_file(demourl)
            unpack_gz(filename)
    else:
        print('no demo url yet')

# get_demos_from_match('1-3ae5df7f-cb2e-467b-bbd1-6d8aa280728e')
# get_demos_from_match('1-95b68b78-45b8-4732-ba05-390a824c1455')