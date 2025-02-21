import git
import os


class GitCleaner:
    def __init__(self, repo_path, branch_name):
        self.repo_path = repo_path
        self.branch_name = branch_name

    def reset_commit(self):
        try:
            os.chdir(self.repo_path)
            repo = git.Repo(self.repo_path)
            repo.git.config("user.email", os.getenv("maill"))
            # 设置用户名
            repo.git.config("user.name", os.getenv("namee"))
            repo.git.checkout('--orphan', 'tmp_branch')
            repo.git.add(A=True)
            repo.git.commit(m="update")
            repo.git.execute(['git', 'branch', '-D', self.branch_name])
            repo.git.execute(['git', 'branch', '-m', self.branch_name])
            repo.git.execute(['git', 'push', '-f', 'origin', self.branch_name])
        except Exception as e:
            print(f'git清理异常: {e}')


if __name__ == "__main__":
    # 这里假设仓库路径为当前工作目录（可根据实际情况修改）
    repo_path = os.getcwd()
    # 要清理历史提交的分支名称，假设为 main 分支（可根据实际情况修改）
    branch_name = "main"
    cleaner = GitCleaner(repo_path, branch_name)
    cleaner.reset_commit()
