#!/usr/bin/python
import cmd2
import getpass
import os
import shlex
import sys
from core.db.connection import *


from optparse import OptionParser

'''
@author: anant bhardwaj
@date: Sep 26, 2013

datahub cli interface
'''
kCmdList = [
    '** Any SQL Query **',
    'mkrepo <repo-name> \t -- to create a new repository',
    'ls \t\t\t -- to list repositories',
    'ls <repo-name> \t\t -- to list tables in a repository',
    'rm <repo-name [-f]> \t\t -- to remove a repository',
]


class DatahubTerminal(cmd2.Cmd):
  def __init__(self):
    usage = "--user <user-name> [--host <host-name>] [--port <port>]"
    parser = OptionParser()
    parser.set_usage(usage)
    parser.add_option("-u", "--user", dest="user", help="databse username")
    parser.add_option("-H", "--host", dest="host", help="database hostname", default="localhost")
    parser.add_option("-p", "--port", dest="port", help="database port", type="int", default=5432)
    (options, args) = parser.parse_args()

    if not options.user:
      parser.print_usage()
      sys.exit(1)

    parser.destroy()
    password = getpass.getpass('password: ')
    cmd2.Cmd.__init__(self, completekey='tab')

    try:
      self.con = Connection(user=options.user, password=password)
      self.prompt = "datahub> "
    except Exception, e:
      self.print_line('error: %s' % (e.message))
      sys.exit(1)

  def do_ls(self, line):
    try:
      repo = line.strip()
      if repo != '':
        res = self.con.list_tables(repo=repo)
        self.print_result(res)
      else:
        res = self.con.list_repos()
        self.print_result(res)

    except Exception, e:
      self.print_line('error: %s' % (e.message))

  def do_mkrepo(self, line):
    try:
      repo = line.strip()
      if repo != '':
        res = self.con.create_repo(repo)
        self.print_result(res)
      else:
        self.print_line("invalid repo name: '%s'" % (repo))

    except Exception, e:
      self.print_line('error: %s' % (e.message))

  def do_rm(self, line):
    try:
      repo = line.strip()
      force = False
      if repo.endswith('-f'):
        force = True
        tokens = repo.split(' ')
        repo = tokens[0].strip()
      if repo != '':
        res = self.con.delete_repo(repo, force)
        self.print_result(res)
      else:
        self.print_line("invalid repo name: '%s'" % (repo))

    except Exception, e:
      self.print_line('error: %s' % ("can't drop the repo, use -f to force drop."))


  def default(self, line):
    try:      
      res = self.con.execute_sql(
          query=line,
          params=None)
      self.print_result(res)
    except Exception, e:
      self.print_line('error: %s' % (e.message))

  def do_exit(self, line):
    return True

  def print_result(self, res):
    if res['row_count'] >= 0:
      col_names = [field['name']
          for field in res['fields']]
      self.print_line('%s' % ('\t'.join(col_names)))
      self.print_line('%s' % (''.join(
          ['------------' for i in range(0, len(col_names))])))
      for row in res['tuples']:
        self.print_line('%s' % ('\t'.join([c for c in row])))

      self.print_line('')
      self.print_line('%s rows returned' % (res['row_count']))
    else:
      self.print_line('%s' % ('success' if res['status'] else 'error'))

  def do_help(self, line): 
    for cmd in kCmdList:
      self.print_line(cmd)

  def print_line(self, line):
    self.stdout.write(line)
    self.stdout.write('\n')

  def completedefault(self, text, line, begidx, endidx):
    pass


def main():  
  datahub_terminal = DatahubTerminal()
  sys.argv = sys.argv[:1]
  datahub_terminal.cmdloop()


if __name__ == '__main__':
  main()
