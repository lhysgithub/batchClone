import argparse
import os, stat
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future

from git import Repo  # gitpython
from github import Github # pygithub
from pathlib import Path
import shutil
import logging

logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(filename=f'log.txt')
fh.setFormatter(formatter)
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)

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
executor = ThreadPoolExecutor(max_workers=2)
future1 = Future()
future2 = Future()


start_epoch = 873

def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)

def bulk_clone_repos():
    global start_epoch
    global future1
    global future2
    def get_dest(git_repo_url: str):
        return os.path.join(args.project_path, git_repo_url.split('/')[-1].split('.git')[0])

    try:
        repos_num = 0
        epoch_num = 0
        for repo in repos:
            epoch_num += 1
            if epoch_num < start_epoch:
                continue
            start_epoch = epoch_num
            repo_name = repo.split('/')[-1].split('.git')[0]
            repo_user = repo.split('/')[-2]
            gitrepo = g.get_repo(repo_user + "/" + repo_name)
            contents = gitrepo.get_contents("")
            isMaven = 0
            for content_file in contents:
                # print(content_file)
                if content_file.path == "pom.xml":
                    isMaven = 1
                    break
            if isMaven == 0:
                continue
            repos_num += 1
            logger.info("epoch_num: {} repos_num: {} Git clone: [{}]".format(epoch_num, repos_num, repo))
            dir_path = get_dest(repo)
            dir = Path(dir_path)
            if dir.exists():
                shutil.rmtree(dir_path, onerror=remove_readonly)
            if args.multi_thread:
                # executor.submit(Repo.clone_from, url=repo, to_path=get_dest(repo))
                # time.sleep(30)
                while 1:
                    print("future1.running: ", future1.running())
                    print("future2.running: ", future2.running())
                    print("future1.exception: ", future1.exception())
                    print("future2.exception: ", future2.exception())
                    if future1._state == 'PENDING':
                        future1 = executor.submit(Repo.clone_from, url=repo, to_path=get_dest(repo))
                        break
                    if future2._state == 'PENDING':
                        future2 = executor.submit(Repo.clone_from, url=repo, to_path=get_dest(repo))
                        break
                    time.sleep(30)
            else:
                Repo.clone_from(url=repo, to_path=get_dest(repo))
    except Exception as error:
        print(error)
        bulk_clone_repos()



if __name__ == "__main__":
    bulk_clone_repos()
