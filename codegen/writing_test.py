#!/usr/local/bin/python

import os
import unittest

import writing


class NoMoreLinesToRead(IndexError):
    pass


class Recorder(object):

    def __init__(self):
        # The last item in the list is appended to until a newline
        # character is read
        self._lines = ['']

    def write(self, text):
        linesToAdd = text.split(writing.kDefaultNewlineChar)
        self._lines[-1] += linesToAdd[0]
        self._lines.extend(linesToAdd[1:])

    def readline(self):
        if len(self._lines) == 1:
            raise NoMoreLinesToRead
        return self._lines.pop(0)

    def readlines(self):
        result = []
        while True:
            try:
                result.append(self.readline())
            except NoMoreLinesToRead:
                return result

    def __iter__(self):
        while len(self._lines) > 1:
            yield self._lines.pop(0)

    def numberOfUnreadLines(self):
        return len(self._lines) - 1


class LineWriterTest(unittest.TestCase):

    def setUp(self):
        self.recorder = Recorder()
        self.writer = writing.LineWriter(self.recorder)

    def testWriteNoLines(self):
        with self.assertRaises(NoMoreLinesToRead):
            self.recorder.readline()

    def testWriteSingleLine(self):
        self.writer.writeLine('Single line')
        self.assertEqual(self.recorder.readline(), 'Single line')
        with self.assertRaises(NoMoreLinesToRead):
            self.recorder.readline()

    def testWriteMultipleLines(self):
        self.writer.writeLine('blah')
        self.writer.writeLine('Where is the beef')
        self.writer.writeLine('Got Milk?')
        self.assertEqual(self.recorder.numberOfUnreadLines(), 3)
        self.assertEqual(
                self.recorder.readlines(),
                ['blah', 'Where is the beef', 'Got Milk?'])
        with self.assertRaises(NoMoreLinesToRead):
            self.recorder.readline()

    def testWriteMultipleLinesInOneCall(self):
        lines = ['aaa', 'bbb', 'ccc', '', 'ddd']
        self.writer.writeLine(writing.kDefaultNewlineChar.join(lines))
        for line in lines:
            self.assertEqual(self.recorder.readline(), line)
        with self.assertRaises(NoMoreLinesToRead):
            self.recorder.readline()

    def testWriteEmptyLine(self):
        self.writer.writeLine('')
        self.assertEqual(self.recorder.readline(), '')
        with self.assertRaises(NoMoreLinesToRead):
            self.recorder.readline()

    def testWriteWithoutNewLine(self):
        self.writer.write('a')
        self.writer.write('b')
        self.writer.writeLine()
        self.writer.write('c')
        self.writer.write('d')
        self.writer.writeLine('e')
        self.assertEqual(self.recorder.readlines(),
            ['ab', 'cde'])


class FileReader(object):

    def __init__(self, filename, file):
        self._filename = filename
        self._file = file
        self._bufferedLines = []
        self._currentLine = 0

    def readline(self):
        if self._file:
            self._closeFileAndReadFileContents()
        if self._currentLine == len(self._bufferedLines):
            raise NoMoreLinesToRead
        result = self._bufferedLines[self._currentLine]
        self._currentLine += 1
        return result

    def readlines(self):
        if self._file:
            self._closeFileAndReadFileContents()
        self._currentLine += len(self._bufferedLines)
        return list(self._bufferedLines)

    def numberOfUnreadLines(self):
        if self._file:
            self._closeFileAndReadFileContents()
        return len(self._bufferedLines) - self._currentLine

    def _closeFileAndReadFileContents(self):
        self._file.close()
        self._file = None
        file = open(self._filename, 'r')
        self._bufferedLines.extend(
                line.rstrip(writing.kDefaultNewlineChar)
                for line in file.readlines())
        file.close()


class FileWriterTest(LineWriterTest):

    def setUp(self):
        self.filename = '/tmp/gmidl_test.txt'
        self.file = open(self.filename, 'w')
        self.recorder = FileReader(self.filename, self.file)
        self.writer = writing.LineWriter(self.file)

    def tearDown(self):
        os.remove(self.filename)


class IndentWriterTest(LineWriterTest):

    def setUp(self):
        self.recorder = Recorder()
        self.writer = writing.IndentWriter(self.recorder)

    def testWriteIndent(self):
        self.writer.writeLine('unindented')
        with self.writer.indent():
            self.writer.writeLine('indented')
        self.writer.writeLine('unindented')
        self.assertEqual(self.recorder.numberOfUnreadLines(), 3)
        self.assertEqual(self.recorder.readline(), 'unindented')
        self.assertEqual(self.recorder.readline(), '    indented')
        self.assertEqual(self.recorder.readline(), 'unindented')

    def testWriteMultilayeredIndent(self):
        def writeLayers(indentAmount, maxIndent):
            self.writer.writeLine('level %d' % indentAmount)
            if indentAmount < maxIndent:
                with self.writer.indent():
                    writeLayers(indentAmount + 1, maxIndent)
        writeLayers(0, 3)
        self.assertEqual(
                self.recorder.numberOfUnreadLines(),
                writing.kDefaultIndentWidth)
        for line in self.recorder:
            numberFromLine = int(line.strip(' ').split(' ')[1])
            self.assertEqual(
                    line,
                    '%slevel %d' % (
                            writing.kDefaultIndentChar
                                    * writing.kDefaultIndentWidth
                                    * numberFromLine,
                            numberFromLine))

    def testMultiIndent(self):
        with self.writer.indent(2):
            self.writer.writeLine('double indent!')
        with self.writer.indent(1):
            self.writer.writeLine('single indent!')
        with self.writer.indent(3):
            self.writer.writeLine('triple indent!')
        with self.writer.indent(1):
            self.writer.writeLine('single indent!')
        self.writer.writeLine('no indent!')
        self.assertEqual(
                self.recorder.readline(),
                '        double indent!')
        self.assertEqual(
                self.recorder.readline(),
                '    single indent!')
        self.assertEqual(
                self.recorder.readline(),
                '            triple indent!')
        self.assertEqual(
                self.recorder.readline(),
                '    single indent!')
        self.assertEqual(
                self.recorder.readline(),
                'no indent!')

    def testIgnoreAndHeedIndent(self):
        def getIndent(line):
            if not line.startswith('    '):
                return 0
            return getIndent(line[writing.kDefaultIndentWidth:]) + 1
        with self.writer.indent():
            self.writer.writeLine('blah')
            with self.writer.ignoreIndent():
                self.writer.writeLine('blah')
                self.writer.writeLine('blah')
            self.writer.writeLine('blah')
            with self.writer.indent():
                self.writer.writeLine('blah')
                with self.writer.ignoreIndent():
                    self.writer.writeLine('blah')
            self.writer.writeLine('blah')
        self.writer.writeLine('blah')
        self.assertEqual(
                [getIndent(line) for line in self.recorder.readlines()],
                [1, 0, 0, 1, 2, 0, 1, 0])

    def testGetRemainingSpaceInLine(self):
        def testIndent(i, maxIndent):
            self.assertEqual(
                    self.writer.getRemainingSpaceInLine(),
                    writing.kDefaultMaxLineWidth
                            - i * len(writing.kDefaultNewlineChar)
                                    * writing.kDefaultIndentWidth)
            if i < maxIndent:
                with self.writer.indent():
                    testIndent(i + 1, maxIndent)
        testIndent(0, 20)


if __name__ == '__main__':
    unittest.main()
