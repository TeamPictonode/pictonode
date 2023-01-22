

# This file was written in its entirety by Parker Nelms and Stephen Foster.

class User:
  """this class is used to hold information about the users account"""

  def __init__(self, name, username, last_login_date):
    self.name = name
    self.username = username
    self.is_logged_in = False
    self.last_login_date = last_login_date


  def set_login_status(self, last_login_date):
    """updates the users last login date, to be updated
    by the daemon and checked by the plugin"""

    self.last_login_date = last_login_date
  

