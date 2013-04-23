#!/usr/bin/env python
from flask.ext.script import Manager
from flask.ext.funnel.manager import manager as funnel_manager
from main import app

manager = Manager(app)
manager.add_command('funnel', funnel_manager)

if __name__ == '__main__':
    manager.run()
