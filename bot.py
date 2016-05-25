import json
from urllib.request import Request, urlopen

headers = {
	'Accept': 'application/json'
}

request = Request('http://api.themoviedb.org/3/search/movie?query=roi&api_key=7721785a65a1f3f7b2ebc76d653a3632', headers=headers)

with urlopen(request) as f:
	js = json.loads(f.read().decode('utf-8'))
	print(js['results'][0])

#http://api.themoviedb.org/3/search/movie?query=lion&api_key=7721785a65a1f3f7b2ebc76d653a3632