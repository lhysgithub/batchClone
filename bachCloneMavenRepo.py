import argparse
import os
from concurrent.futures import ThreadPoolExecutor

from git import Repo  # gitpython
from github import Github


argparser = argparse.ArgumentParser("批量下载Git Repos")

argparser.add_argument("-p", "--project-path", type=str, required=True, help="项目地址，所有批量下载的repos都会存在这个目录下。")
argparser.add_argument("-m", "--multi-thread", type=int,  required=True, help="开启多线程，默认False")
argparser.add_argument("-r", "--repos-file", type=str, required=True, help="想要clone的仓库地址")

args = argparser.parse_args()

# get repos
repos = []
with open(args.repos_file) as f:
    lines = f.readlines()
    for line in lines:
        repos.append(line.split(',')[2])

# using access_token create github case
g = Github("ghp_1fPXYOqTXEQNX27U9zv9QmyKB5nv1Pp2zYV6V")

def bulk_clone_repos():

    def get_dest(git_repo_url: str):
        return os.path.join(args.project_path, git_repo_url.rsplit(".", maxsplit=1)[0].rsplit("/", maxsplit=1)[1])

    executor = ThreadPoolExecutor(max_workers=10)
    repos_num = 0
    epoch_num = 0
    for repo in repos:
        epoch_num += 1
        repo_name = repo.split('.')[-2].split('/')[-1]
        repo_user = repo.split('.')[-2].split('/')[-2]
        gitrepo = g.get_repo(repo_user+"/"+repo_name)
        contents = gitrepo.get_contents("")
        isMaven = 0
        for content_file in contents:
            # print(content_file)
            if content_file.path == "pom.xml":
                isMaven = 1
                break
        if isMaven == 0:
            continue
        repos_num +=1
        print("epoch_num: {} repos_num: {} Git clone: [{}]".format(epoch_num, repos_num, repo))
        if args.multi_thread:
            executor.submit(Repo.clone_from, repo, get_dest(repo))
        else:
            Repo.clone_from(url=repo, to_path=get_dest(repo))

if __name__ == "__main__":
    bulk_clone_repos()
