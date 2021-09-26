''' mass modules updater '''
from subprocess import call
from pkg_resources import working_set

packages = [dist.project_name for dist in working_set]
call("pip install --upgrade " + ' '.join(packages), shell=True)
