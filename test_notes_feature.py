import contextlib
import io
import sys
import types
import unittest
from unittest.mock import patch


sys.modules.setdefault(
    "voice",
    types.SimpleNamespace(listen=lambda: "")
)
sys.modules.setdefault(
    "wake_word",
    types.SimpleNamespace(wait_for_wake_word=lambda: True)
)

import main
import notes


SAMPLE_NOTES = (
    "testing for test||Notes||iCloud\n"
    "Sahya||Notes||iCloud\n"
    "Sahya||ECS||iCloud\n"
    "Old Test||Recently Deleted||iCloud\n"
)

SAMPLE_FOLDERS = (
    "iCloud||Notes\n"
    "iCloud||APs\n"
    "iCloud||college\n"
    "iCloud||ECS\n"
    "iCloud||Imp Study Notes\n"
    "iCloud||Quick Notes\n"
    "iCloud||SCHEDULE\n"
    "iCloud||Recently Deleted\n"
)


class CommandRoutingTests(unittest.TestCase):
    def set_inputs(self, items):
        main.input_queue = main.queue.Queue()

        for item in items:
            main.input_queue.put(item)

    def check_routes(self, commands, function_name, marker):
        with patch.object(main, function_name, return_value=marker):
            for command in commands:
                with self.subTest(command=command):
                    self.assertEqual(main.handle_commands(command), marker)

    def test_notes_command_aliases_route_to_expected_handlers(self):
        self.check_routes(
            main.CREATE_NOTE_COMMANDS,
            "create_note_interactive",
            "created"
        )
        self.check_routes(
            main.SHOW_NOTE_COMMANDS,
            "show_notes_interactive",
            "shown"
        )
        self.check_routes(
            main.FIND_NOTE_COMMANDS,
            "find_note_interactive",
            "found"
        )
        self.check_routes(
            main.APPEND_NOTE_COMMANDS,
            "append_note_interactive",
            "appended"
        )
        self.check_routes(
            main.DELETE_NOTE_COMMANDS,
            "delete_note_interactive",
            "deleted"
        )
        self.check_routes(
            main.OPEN_NOTE_COMMANDS,
            "open_note_interactive",
            "opened"
        )

    def test_direct_delete_refuses_deleted_note(self):
        with patch.object(
            main,
            "find_notes",
            return_value=[
                {
                    "name": "Old Test",
                    "folder": "Recently Deleted",
                    "deleted": True
                }
            ]
        ):
            self.assertEqual(
                main.handle_commands("delete Old Test"),
                "I can't modify notes in Recently Deleted."
            )

    def test_direct_delete_asks_for_folder_when_name_is_duplicated(self):
        matches = [
            {"name": "Sahya", "folder": "Notes", "deleted": False},
            {"name": "Sahya", "folder": "ECS", "deleted": False}
        ]

        with patch.object(main, "find_notes", return_value=matches):
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = main.handle_commands("delete Sahya")

            self.assertEqual(result, "Please specify the folder.")
            self.assertIn("[Notes] Sahya", output.getvalue())
            self.assertIn("[ECS] Sahya", output.getvalue())

    def test_text_input_is_not_echoed_twice(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            main.display_command("text", "create note")

        self.assertEqual(output.getvalue(), "")

    def test_voice_input_is_echoed_once(self):
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            main.display_command("voice", "create note")

        self.assertEqual(output.getvalue(), "> create note\n")

    def test_create_note_accepts_mixed_text_then_voice_inputs(self):
        self.set_inputs([
            ("voice", "Sahya Test"),
            ("text", "Notes"),
            ("voice", "This was created using mixed input.")
        ])

        with patch.object(main, "create_note", return_value="success||Notes") as create:
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = main.handle_commands("create note")

        self.assertEqual(result, "Note created in Notes.")
        create.assert_called_once_with(
            "Sahya Test",
            "This was created using mixed input.",
            "Notes"
        )
        self.assertIn("> Sahya Test", output.getvalue())
        self.assertIn("> This was created using mixed input.", output.getvalue())

    def test_create_note_accepts_mixed_voice_then_text_inputs(self):
        self.set_inputs([
            ("text", "Mixed Test"),
            ("voice", "ECS"),
            ("text", "Testing mixed voice and text.")
        ])

        with patch.object(main, "create_note", return_value="success||ECS") as create:
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = main.handle_commands("new node")

        self.assertEqual(result, "Note created in ECS.")
        create.assert_called_once_with(
            "Mixed Test",
            "Testing mixed voice and text.",
            "ECS"
        )
        self.assertIn("> ECS", output.getvalue())

    def test_create_note_default_folder_aliases_pass_no_folder(self):
        for folder in ["none", "default", "None.", "Default."]:
            with self.subTest(folder=folder):
                self.set_inputs([
                    ("text", "Default Test."),
                    ("text", folder),
                    ("text", "What day is it today?")
                ])

                with patch.object(
                    main,
                    "create_note",
                    return_value="success||Notes"
                ) as create:
                    output = io.StringIO()

                    with contextlib.redirect_stdout(output):
                        result = main.handle_commands("create note")

                self.assertEqual(result, "Note created in Notes.")
                create.assert_called_once_with(
                    "Default Test",
                    "What day is it today?",
                    None
                )

    def test_create_note_command_tolerates_voice_punctuation(self):
        self.set_inputs([
            ("voice", "Hello."),
            ("voice", "None."),
            ("voice", "What day is it today?")
        ])

        with patch.object(main, "create_note", return_value="success||Notes") as create:
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = main.handle_commands("Create note.")

        self.assertEqual(result, "Note created in Notes.")
        create.assert_called_once_with(
            "Hello",
            "What day is it today?",
            None
        )

    def test_open_notes_opens_notes_app(self):
        with patch.object(main, "open_application") as open_application:
            self.assertEqual(
                main.handle_commands("open notes"),
                "Opening Notes."
            )

        open_application.assert_called_once_with("Notes")


class NotesBackendTests(unittest.TestCase):
    def fake_script(self, script):
        if "folderList" in script and "currentNote" not in script:
            return SAMPLE_FOLDERS

        return SAMPLE_NOTES

    def test_get_notes_supports_all_folder_aliases(self):
        with patch.object(notes, "run_script", side_effect=self.fake_script):
            for folder in [
                "all",
                "all iCloud",
                "everywhere",
                "all notes",
                "all notes."
            ]:
                with self.subTest(folder=folder):
                    self.assertEqual(len(notes.get_notes(folder)), 4)

    def test_get_notes_filters_folders_case_insensitively(self):
        with patch.object(notes, "run_script", side_effect=self.fake_script):
            ecs_notes = notes.get_notes("ecs.")

        self.assertEqual(
            ecs_notes,
            [
                {
                    "name": "Sahya",
                    "folder": "ECS",
                    "account": "iCloud",
                    "deleted": False
                }
            ]
        )

    def test_show_notes_marks_recently_deleted(self):
        with patch.object(notes, "run_script", side_effect=self.fake_script):
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = notes.show_notes_interactive(lambda _: "all")

        self.assertEqual(result, "Those are the notes I found.")
        self.assertIn("[Recently Deleted - DELETED]", output.getvalue())

    def test_find_duplicate_note_lists_possible_folders(self):
        with patch.object(notes, "run_script", side_effect=self.fake_script):
            answers = iter(["all", "Sahya"])
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = notes.find_note_interactive(lambda _: next(answers))

        self.assertEqual(result, "Please specify the folder.")
        self.assertIn("[Notes] Sahya", output.getvalue())
        self.assertIn("[ECS] Sahya", output.getvalue())

    def test_create_note_refuses_nonexistent_folder(self):
        with patch.object(notes, "run_script", side_effect=self.fake_script):
            self.assertEqual(
                notes.create_note("Title", "Body", "banana"),
                "folder_not_found"
            )

    def test_create_note_default_uses_notes_app_default_location(self):
        scripts = []

        def capture_script(script):
            scripts.append(script)
            return "success"

        with patch.object(notes, "run_script", side_effect=capture_script):
            self.assertEqual(
                notes.create_note("Title", "Body", None),
                "success"
            )

        self.assertIn("make new note with properties", scripts[0])
        self.assertNotIn("folderList", scripts[0])

    def test_open_note_refuses_recently_deleted(self):
        with patch.object(
            notes,
            "find_notes",
            return_value=[
                {
                    "name": "Old Test",
                    "folder": "Recently Deleted",
                    "deleted": True
                }
            ]
        ):
            self.assertEqual(
                notes.open_note("Old Test", "Recently Deleted"),
                "deleted"
            )


if __name__ == "__main__":
    unittest.main()
