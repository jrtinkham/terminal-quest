#!/usr/bin/env python

# linux-story-gui
#
# Copyright (C) 2014, 2015 Kano Computing Ltd
# License: GNU GPL v2 http://www.gnu.org/licenses/gpl-2.0.txt
#
# Launches linux tutorial in a Gtk application

import os
import sys
import threading
import socket
import Queue
from gi.repository import Gtk, Gdk, GLib
import time
import subprocess

if __name__ == '__main__' and __package__ is None:
    dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if dir_path != '/usr':
        sys.path.insert(1, dir_path)

from linux_story.socket_functions import create_server
from linux_story.gtk3.TerminalUi import TerminalUi
from linux_story.gtk3.Spellbook import Spellbook
from linux_story.gtk3.Storybook import Storybook
from linux_story.gtk3.FinishDialog import FinishDialog
from linux_story.common import css_dir
from linux_story.gtk3.MenuScreen import MenuScreen
from linux_story.load_defaults_into_filetree import (
    revert_to_default_permissions
)

from kano.gtk3.apply_styles import apply_styling_to_screen
from kano.gtk3.scrolled_window import ScrolledWindow


class GenericWindow(Gtk.Window):
    CSS_FILE = os.path.join(
        css_dir,
        "style.css"
    )
    COLOUR_CSS_FILE = os.path.join(
        css_dir,
        "colours.css"
    )

    def __init__(self):
        apply_styling_to_screen(self.CSS_FILE)
        apply_styling_to_screen(self.COLOUR_CSS_FILE)

        Gtk.Window.__init__(self)
        self.connect('delete-event', self.close_window)
        self.get_style_context().add_class("main_window")
        self.maximize()
        self.set_title("Terminal Quest")
        self.set_icon_name("linux-story")


class MainWindow(GenericWindow):
    '''Window class that contains all the elements in the application
    '''

    def __init__(self, debug=False):
        GenericWindow.__init__(self)

        # This decides whether the spellbook and terminal are hidden
        # Should also write to logs.
        self.debug = debug

    def set_cursor_invisible(self, *_):
        blank_cursor = Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR)
        self.get_window().set_cursor(blank_cursor)

    def setup_application_widgets(self):
        screen = Gdk.Screen.get_default()
        width = screen.get_width()
        height = screen.get_height()

        self.terminal = TerminalUi()
        fg_color = Gdk.Color.parse("#ffffff")[1]
        bg_color = Gdk.Color.parse("#262626")[1]
        self.terminal.set_colors(fg_color, bg_color, [])
        self.terminal.set_margin_top(10)
        self.terminal.set_margin_left(10)
        self.terminal.set_margin_right(10)

        self.spellbook = Spellbook()

        self.story = Storybook(
            width / 2 - 40,
            height - self.spellbook.HEIGHT - 2 * 44 - 10
        )
        self.story.set_margin_top(10)
        self.story.set_margin_left(10)
        self.story.set_margin_right(10)

        story_sw = ScrolledWindow()
        story_sw.apply_styling_to_screen()
        story_sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        story_sw.add(self.story)

        left_background = Gtk.EventBox()
        left_background.get_style_context().add_class("story_background")
        right_background = Gtk.EventBox()
        right_background.get_style_context().add_class("terminal_background")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        hbox = Gtk.Box()

        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(self.spellbook, False, False, 0)
        hbox.pack_start(left_background, False, False, 0)
        hbox.pack_start(right_background, False, False, 0)

        left_background.add(story_sw)
        right_background.add(self.terminal)

        # Allow for margin on bottom
        # TODO: this is hacky. Tidy up.
        self.terminal.set_size_request(
            width / 2 - 20, height - self.spellbook.HEIGHT - 2 * 44 - 20
        )
        story_sw.set_size_request(
            width / 2 - 20, height - self.spellbook.HEIGHT - 2 * 44 - 10
        )

        self.run_server()

    def close_window(self, widget=None, event=None):
        '''
        Shut the server down and kils application

        Args:
            widget (Gtk.Widget)
            event (Gdk.EventButton)

        Returns:
            None
        '''

        if hasattr(self, "server"):
            self.server.socket.shutdown(socket.SHUT_RDWR)
            self.server.socket.close()
            self.server.shutdown()

        # Do this AFTER the server shutdown, so if this goes wrong,
        # we can quickly relaunch TQ.
        revert_to_default_permissions()

        Gtk.main_quit()

    def finish_app(self, widget=None, event=None):
        '''
        After user has finished running the application, show a dialog and
        close the window

        Args:
            widget (Gtk.Widget)
            event (Gdk.EventButton)

        Returns:
            None
        '''

        kdialog = FinishDialog()
        response = kdialog.run()

        if response == 'feedback':
            subprocess.Popen('/usr/bin/kano-feedback')

        self.close_window()

    # TODO: this should be a private member function, and probably
    # should have a different name
    def create_terminal(self, challenge_number="", step_number=""):
        '''
        This function currently creates the thread that runs the
        storyline in the TerminalUi class and attaches an event listener
        to update the UI when the queue is updated.

        Args:
            challenge_number (str): The challenge number of the challenge that
                                    we want to start from.
            step_number (str): The step number of the challenge that
                               we want to start from.

        Returns:
            None
        '''

        if os.path.dirname(__file__).startswith('/usr'):
            filepath = '/usr/bin/linux-story'
        else:
            filepath = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../bin/linux-story"
                )
            )

        command = (
            "python " +
            filepath + " " +
            challenge_number + " " +
            step_number
        )

        self.terminal.launch_command(command)

        GLib.idle_add(self.check_queue)
        self.show_all()

        # This to hide the spellbook and terminal from view until the story has
        # finished displaying.
        # In debug mode, we don't want to hide it.
        if not self.debug:
            self.terminal.hide()
            self.spellbook.hide()

    def type_text(self, text):
        '''Wrapper function for the story member variable
        '''
        self.story.type_coloured_text(text)

    def print_challenge_title(self, number):
        '''Prints the ascii art challenge title at the start
        '''

        self.story.print_challenge_title(number)

    def print_coloured_text(self, text):
        self.story.print_coloured_text(text)

    def repack_spells(self, spells):
        '''Wrapper function for repacking the spells
        '''

        self.spellbook.repack_spells(spells)

    def show_terminal(self):
        '''Wrapper function for showing terminal
        Only used at the beginning after story has loaded
        '''

        self.terminal.show_all()
        self.terminal.set_sensitive(True)
        self.terminal.grab_focus()

    def stop_typing_in_terminal(self):
        '''Wrapper function to stop people typing in terminal
        while story or hint is being shown
        '''

        self.terminal.set_sensitive(False)

    def run_server(self):
        '''Start the server
        Create the queue which has length 1, and run it on a separate thread
        '''

        self.queue = Queue.Queue(1)
        self.server = create_server(self.queue)
        t = threading.Thread(target=self.server.serve_forever)
        t.daemon = True
        t.start()

    def check_queue(self, widget=None, event=None, user_data=False):
        '''Check the queue for any updates on what the current challenge is
        '''

        try:
            # Give it a timeout so it doesn't hang indefinitely
            data_dict = self.queue.get(user_data, timeout=5.0)

            if 'exit' in data_dict.keys():
                self.finish_app()

            # Type out the hint
            elif 'hint' in data_dict.keys():
                self.stop_typing_in_terminal()
                self.type_text(data_dict['hint'])
                self.show_terminal()

            else:
                self.story.clear()

                if 'challenge' in data_dict.keys() and \
                   'story' in data_dict.keys() and \
                   'spells' in data_dict.keys():

                    self.stop_typing_in_terminal()

                    # Print the challenge title at the top of the screen
                    challenge = data_dict['challenge']

                    # If challenge is passed, then print a title
                    self.print_challenge_title(challenge)

                    # So the xp is not hardcoded in the story
                    if 'xp' in data_dict and data_dict['xp']:
                        self.type_text(data_dict['xp'])

                    # If we have have just used echo in the previous
                    # challenge, we should print out the user's choice
                    if "print_text" in data_dict and data_dict["print_text"]:
                        # Automatically stick a double newline at the end of
                        # the user text to save us having to do it ourselves.
                        self.print_coloured_text(data_dict["print_text"] + "\n\n")

                    # Type the story out
                    self.type_text(data_dict['story'])

                    # Repack the spells into the spellbook
                    spells = data_dict['spells']
                    self.repack_spells(spells)

                    # Refresh terminal - useful for the first challenge
                    self.show_terminal()
                    self.show_all()

        except Queue.Empty:
            pass
        finally:
            time.sleep(0.02)
            return True

    def show_menu(self):
        self.menu = MenuScreen()
        self.menu.connect(
            'challenge_selected', self.replace_menu_with_challenge
        )
        self.add(self.menu)
        self.show_all()

    def replace_menu_with_challenge(self, widget, challenge_number):
        self.remove(self.menu)
        self.setup_application_widgets()
        self.create_terminal(str(challenge_number), "1")
