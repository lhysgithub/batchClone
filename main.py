import time
from urllib.request import urlopen
from urllib.request import Request
import json


def get_results(search, headers, page, up_stars, down_stars):
    url = 'https://api.github.com/search/repositories?q={search}+stars:{down_stars}..{up_stars}&page={num}&per_page=100&sort=stars' \
          '&order=desc'.format(search=search, num=page, up_stars=up_stars, down_stars=down_stars)
    req = Request(url, headers=headers)
    response = urlopen(req).read()
    result = json.loads(response.decode())
    return result


if __name__ == '__main__':
    # Specify JavaScript Repository
    search = 'language:java'

    # Modify the GitHub token value
    headers = {'User-Agent': 'Mozilla/5.0',
               'Authorization': 'token ghp_1fPXYOqTXEQNX27U9zv9QmyKB5nv1Pp2zYV6V',
               'Content-Type': 'application/json',
               'Accept': 'application/json'
               }

    count = 1
    # The highest value of JavaScript repository STAR is 321701, repository is freeCodeCamp.
    up_stars = 1000000000
    down_stars = 100
    lower_bound = down_stars
    filename = "test.txt"
    fp = open(filename, "w", encoding="utf-8")
    fp.close()
    for i in range(0, 200):
        repos_list = []
        stars_list = []
        for page in range(1, 11):
            results = get_results(search, headers, page, up_stars, down_stars)
            for item in results['items']:
                if item["stargazers_count"] < lower_bound:
                    break
                repos_list.append([count, item["name"], item["clone_url"], item["stargazers_count"]])
                stars_list.append(item["stargazers_count"])
                count += 1
            print("repos:", len(repos_list))

        if len(repos_list) == 0:
            break

        up_stars = stars_list[-1]
        print("up_stars:", up_stars)

        with open(filename, "a", encoding="utf-8") as f:
            for j in range(len(repos_list)):
                f.write(str(repos_list[j][0]) + "," + repos_list[j][1] + "," + repos_list[j][2] + "," + str(repos_list[j][3])
                        + "\n")

        # For authenticated requests, 30 requests per minute
        # For unauthenticated requests, the rate limit allows you to make up to 10 requests per minute.
        time.sleep(60)

