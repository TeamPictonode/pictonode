import unittest
import sys
import os
import threading
import time
import urllib.request
import random
import string

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# autopep8 off
import gi  # noqa

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk # noqa

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf

gi.require_version("Gio", "2.0")
from gi.repository import Gio  # noqa
# autopep8 on

class TestBase(unittest.TestCase):
    # https://stackoverflow.com/a/33353987
    def _assert_logs(self, expr, msg=None):
        if expr:                                                                                       
            print("PASS : {0}".format(msg))                                                     
        else:                                                                                          
            print("FAIL : {0}".format(msg))

    def assertNotIn(self, member, container, msg=None, expected=None,                                     
                 actual=None):                                                                                                                                                               
        msg = msg + " | Expected: {0} | Actual: {1}".format(expected, actual)                                             
        self._assert_logs(member not in container, msg)                                                    
        super(TestBase, self).assertNotIn(member, container, msg)

    def assertEqual(self, first, second, msg=None, expected=None,                                     
                 actual=None):                                                                                                                                                               
        msg = msg + " | Expected: {0} | Actual: {1}".format(expected, actual)                                            
        self._assert_logs(first == second, msg)                                                    
        super(TestBase, self).assertEqual(first, second, msg)

    def assertGreaterEqual(self, first, second, msg=None, expected=None,                                     
                 actual=None):                                                                                                                                                               
        msg = msg + " | Expected: {0} | Actual: {1}".format(expected, actual)                                            
        self._assert_logs(first >= second, msg)                                                    
        super(TestBase, self).assertGreaterEqual(first, second, msg)

class TestToolbarState(TestBase):

    def test_toolbar_state(self, msg=None):
        from pictonode import toolbar

        project_urls = {"Grace": "https://avatars.githubusercontent.com/u/64381571?v=4",
                            "John": "https://avatars.githubusercontent.com/u/19805233?v=4",
                            "Parker": "https://avatars.githubusercontent.com/u/87922675?v=4",
                            "Stephen": "https://avatars.githubusercontent.com/u/67705843?v=4"}
        
        project_images = {}
        for person in project_urls.keys():
            loader = GdkPixbuf.PixbufLoader.new_with_type('jpeg')
            with urllib.request.urlopen(project_urls.get(person)) as f:
                loader.write(f.read())
                pixbuf = loader.get_pixbuf()
                project_images.update({person:pixbuf})
                loader.close()

        toolbar = toolbar.ProjectToolbar("Debug")
        t = threading.Thread(target=Gtk.main, args=())
        toolbar.show_all()

        t.start()

        time.sleep(2)
        for person, image in project_images.items():
            toolbar.add_project(person, image.scale_simple(64, 64, GdkPixbuf.InterpType.BILINEAR))
        
        self.assertEqual(4, len(toolbar._projects), msg="ADD PROJECTS", expected=4, actual=len(toolbar._projects))
        time.sleep(2)

        random.seed()
        index_to_remove = random.randint(0,3)
        project = toolbar._projects[index_to_remove]
        toolbar.remove_project(project)
        self.assertEqual(3, len(toolbar._projects), msg="REMOVE PROJECTS", expected=3, actual=len(toolbar._projects))
        time.sleep(2)

        width_before = toolbar.get_size()[0]
        for project_name, image in project_images.items():
            image = image.scale_simple(128, 128, GdkPixbuf.InterpType.BILINEAR)
            toolbar.update_project_thumbnail(project_name, image)

        self.assertGreaterEqual(toolbar.get_size()[0], width_before, msg="UPDATE THUMBNAILS", expected=">={0}".format(width_before), actual=toolbar.get_size()[0])
        time.sleep(2)

        new_names = []
        for project_name in toolbar._projects:
            new_name = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(1, 10)))
            toolbar.update_project_name(project_name, new_name)
            new_names.append(new_name)

        for project_name in project_urls.keys():
            self.assertNotIn(project_name, toolbar._projects, msg="UPDATE PROJECT NAMES", expected=", ".join(new_names), actual=", ".join(toolbar._projects))
        time.sleep(2)
        
        toolbar.emit("destroy")
        t.join()

if __name__ == '__main__':
    unittest.main()