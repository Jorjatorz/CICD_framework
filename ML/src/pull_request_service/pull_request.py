# Class of an accepted Pull Request. The only required element must be the merge date.
class PullRequest:
    def __init__(self, merge_date):
        self.merge_date = merge_date