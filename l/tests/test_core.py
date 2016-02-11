from io import BytesIO
from textwrap import dedent
from unittest import TestCase

from bp.memory import MemoryFS, MemoryPath

from l import core, cli


class TestOutputters(TestCase):
    def setUp(self):
        self.fs = MemoryFS()
        self.root = MemoryPath(fs=self.fs, path=("test-dir",))
        self.root.createDirectory()

    def assertOutputs(self, result, **kwargs):
        kwargs.setdefault("recurse", core.flat)
        stdout = BytesIO()
        cli.run(stdout=stdout, **kwargs)
        self.assertEqual(stdout.getvalue(), dedent(result).strip("\n") + "\n")

    def children(self, *new, **kwargs):
        of = kwargs.pop("of", self.root)
        assert not kwargs

        of.createDirectory()
        for child in new:
            path = of.child(child)
            path.setContent("")
            yield path

    def test_it_lists_directories(self):
        foo, bar = self.children("foo", "bar")
        self.assertOutputs(
            output=core.columnized,
            paths=[self.root],
            result="bar  foo",
        )

    def test_it_lists_multiple_directories(self):
        one = self.root.child("one")
        two, four = self.children("two", "four", of=one)

        three, = self.children("three")

        self.assertOutputs(
            output=core.columnized,
            paths=[self.root, one],
            result="""
            /mem/test-dir:
            one  three

            /mem/test-dir/one:
            four  two
            """,
        )


    def test_it_ignores_hidden_files_by_default(self):
        foo, hidden = self.children("foo", ".hidden")
        self.assertOutputs(
            output=core.columnized,
            paths=[self.root],
            result="foo",
        )

    def test_it_ignores_hidden_files_by_default_for_multiple_directories(self):
        one = self.root.child("one")
        two, four = self.children(".two", "four", of=one)

        three, = self.children(".three")

        self.assertOutputs(
            output=core.columnized,
            paths=[self.root, one],
            result="""
            /mem/test-dir:
            one

            /mem/test-dir/one:
            four
            """,
        )

    def test_it_can_list_almost_everything(self):
        one = self.root.child("one")
        two, four = self.children(".two", "four", of=one)

        three, = self.children(".three")

        self.assertOutputs(
            ls=core.ls_almost_all,
            output=core.columnized,
            paths=[self.root, one],
            result="""
            /mem/test-dir:
            .three  one

            /mem/test-dir/one:
            .two  four
            """,
        )

    def test_it_can_list_everything(self):
        one = self.root.child("one")
        two, four = self.children(".two", "four", of=one)

        three, = self.children(".three")

        self.assertOutputs(
            ls=core.ls_all,
            output=core.columnized,
            paths=[self.root, one],
            result="""
            /mem/test-dir:
            .  ..  .three  one

            /mem/test-dir/one:
            .  ..  .two  four
            """,
        )

    def test_it_lists_directories_one_per_line(self):
        foo, bar = self.children("foo", "bar")
        self.assertOutputs(
            output=core.one_per_line,
            paths=[self.root],
            result="bar\nfoo\n",
        )

    def test_it_lists_multiple_absolute_directories_one_per_line(self):
        one = self.root.child("one")
        two, four = self.children("two", "four", of=one)

        three, = self.children("three")

        self.assertOutputs(
            output=core.one_per_line,
            paths=[self.root, one],
            result="""
            /mem/test-dir/one
            /mem/test-dir/one/four
            /mem/test-dir/one/two
            /mem/test-dir/three
            """,
        )

    def test_it_lists_directories_recursively(self):
        one = self.root.child("one")
        two, four = self.children("two", "four", of=one)

        three, = self.children("three")
        self.assertOutputs(
            output=core.columnized,
            recurse=core.recurse,
            paths=[self.root],
            result="""
            /mem/test-dir:
            one  three

            /mem/test-dir/one:
            four  two
            """,
        )

    def test_it_lists_directories_recursively_one_per_line(self):
        one = self.root.child("one")
        two, four = self.children("two", "four", of=one)

        three, = self.children("three")
        self.assertOutputs(
            output=core.one_per_line,
            recurse=core.recurse,
            paths=[self.root],
            result="""
            /mem/test-dir/one
            /mem/test-dir/one/four
            /mem/test-dir/one/two
            /mem/test-dir/three
            """,
        )
