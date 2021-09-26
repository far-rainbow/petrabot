<<<<<<< HEAD
import pkg_resources
from subprocess import call

packages = [dist.project_name for dist in pkg_resources.working_set]
call("pip install --upgrade " + ' '.join(packages), shell=True)
=======
''' mass modules updater '''
from subprocess import call
from pkg_resources import working_set

packages = [dist.project_name for dist in working_set]
call("pip install --upgrade " + ' '.join(packages), shell=True)
>>>>>>> refs/heads/master
