#!/usr/bin/env python
import os
import site


ROOT = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.abspath(os.path.join(ROOT, '../../')))


from flask.ext.script import Manager
from flask.ext.funnel.manager import manager as funnel_manager
from main import app


manager = Manager(app)
manager.add_command('funnel', funnel_manager)

if __name__ == '__main__':
    manager.run()
