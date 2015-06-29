#!/usr/bin/env python
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A chapter of the story


from linux_story.story.terminals.terminal_bernard import TerminalMkdirBernard
from linux_story.story.challenges.challenge_27 import Step1 as NextStep
from linux_story.step_helper_functions import unblock_cd_commands


class StepTemplateMkdir(TerminalMkdirBernard):
    challenge_number = 26


class Step1(StepTemplateMkdir):
    story = [
        "You are back in town. Have a {{lb:look around}}."
    ]

    start_dir = "~/town/east"
    end_dir = "~/town/east"

    hints = [
        "{{rb:Use}} {{yb:ls}} {{rb:to look around.}}"
    ]

    commands = [
        "ls",
        "ls -a"
    ]

    deleted_items = ["~/town/east/shed-shop/Eleanor"]
    story_dict = {
        "Eleanor": {
            "path": "~/town/east"
        }
    }
    eleanors_speech = "Eleanor: {{Bb:The library is over there!}}"

    def next(self):
        Step2()


class Step2(StepTemplateMkdir):
    story = [
        "You see the {{lb:library}} ahead.",

        "Eleanor: {{Bb:There it is! The}} {{bb:library}} "
        "{{Bb:is right there! Let's}} {{lb:go inside.}}"
    ]

    start_dir = "~/town/east"
    end_dir = "~/town/east/library"

    hints = [
        "{{rb:Use}} {{yb:cd library/}} {{rb:to go inside the library.}}"
    ]
    eleanors_speech = "Eleanor: {{Bb:I love the library! Let's go inside!}}"

    def block_command(self):
        return unblock_cd_commands(self.last_user_input)

    def next(self):
        Step3()


class Step3(StepTemplateMkdir):
    story = [
        "Eleanor skips into the library, while you follow her.",
        "{{lb:Look around}} the library."
    ]

    start_dir = "~/town/east/library"
    end_dir = "~/town/east/library"

    hints = [
        "{{rb:Use}} {{yb:ls}} {{rb:to look around.}}"
    ]
    commands = [
        "ls",
        "ls -a"
    ]
    deleted_items = ["~/town/east/Eleanor"]
    story_dict = {
        "Eleanor": {
            "path": "~/town/east/library"
        }
    }
    eleanors_speech = "Eleanor: {{Bb:It's all echo-y-y-y-y..}}"

    def next(self):
        Step4()


class Step4(StepTemplateMkdir):
    story = [
        "You're in a large open space, with two clearly sections, "
        "one labelled}} {{bb:public-section}}{{lb:, one labelled}} "
        "{{bb:private-section}}{{lb:.}}",

        "Eleanor: {{Bb:There used to be a librarian here.",

        "She would tell me off for trying to look in the}} "
        "{{bb:private-section}}.",

        "{{Bb:What do you think is in there?  Let's try and}} "
        "{{lb:look inside}}{{Bb:.}}"
    ]

    start_dir = "~/town/east/library"
    end_dir = "~/town/east/library"

    commands = [
        "ls private-section/",
        "ls private-section"
    ]

    hints = [
        "{{rb:Use}} {{yb:ls private-section/}} {{rb:to look in the "
        "private-section of the library.}}"
    ]
    eleanors_speech = "Eleanor: {{Bb:What's in the private-section?}}"

    def next(self):
        Step5()


class Step5(StepTemplateMkdir):

    story = [
        "Eleanor: {{Bb:I guess the private-section is locked to outsiders...",

        "Let's see if we can find something useful in the}} "
        "{{bb:public section.}}",

        "\nUse {{lb:ls}} to look in the {{lb:public-section}}."
    ]

    start_dir = "~/town/east/library"
    end_dir = "~/town/east/library"
    commands = [
        "ls public-section",
        "ls public-section/",
        "ls -a public-section",
        "ls -a public-section/"
    ]
    hints = [
        "{{rb:Use}} {{lb:ls}} {{rb:to look in the public section.}}",
        "{{rb:Use}} {{yb:ls public-section}} {{rb:to look in the public-"
        "section.}}"
    ]
    eleanors_speech = "Eleanor: {{Bb:What's in the public-section?}}"

    def next(self):
        Step6()


class Step6(StepTemplateMkdir):
    story = [
        "Eleanor: {{Bb:Wow, all the commands have disappeared.",
        "I wonder if people have been stealing them?}}",

        "{{Bb:What is that}} {{lb:NANO}} {{Bb:paper?}}",
        "{{Bb:Let's}} {{lb:examine}} {{Bb:it.}}"
    ]
    start_dir = "~/town/east/library"
    end_dir = "~/town/east/library"
    commands = [
        "cat public-section/NANO"
    ]
    hints = [
        "{{rb:Examine the NANO script with}} {{yb:cat public-section/NANO}}"
    ]
    eleanors_speech = (
        "Eleanor: {{Bb:The library should probably have introduced late "
        "fees.}}"
    )

    def next(self):
        Step7()


class Step7(StepTemplateMkdir):
    story = [
        "Eleanor: {{Bb:So nano allows you to "
        "edit files?}}",

        "{{Bb:Maybe we could use this to fix that "
        "best-horn-in-the-world.sh script?}}",

        "{{Bb:Let's}} {{lb:head back}} {{Bb:to the}} {{lb:shed-shop}}{{Bb:.}}"
    ]
    start_dir = "~/town/east/library"
    end_dir = "~/town/east/shed-shop"
    eleanors_speech = (
        "Bernard: {{Bb:...do we have to go and see creepy Bernard again?}}"
    )
    last_step = True

    def block_command(self):
        return unblock_cd_commands(self.last_user_input)

    def next(self):
        NextStep(self.xp)
