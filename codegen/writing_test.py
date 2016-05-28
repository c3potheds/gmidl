#!/usr/local/bin/python

import os
import unittest

import writing


kNewlineChar = '\n'
kIndentWidth = 4


class NoMoreLinesToRead(IndexError):
	pass


class Recorder(object):

	def __init__(self):
		self._lines = []

	def write(self, text):
		self._lines.extend(text.split(kNewlineChar)[:-1])

	def readline(self):
		if len(self._lines) == 0:
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
		while self._lines:
			yield self._lines.pop(0)

	def numberOfUnreadLines(self):
		return len(self._lines)


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
		self.writer.writeLine(kNewlineChar.join(lines))
		for line in lines:
			self.assertEqual(self.recorder.readline(), line)
		with self.assertRaises(NoMoreLinesToRead):
			self.recorder.readline()

	def testWriteEmptyLine(self):
		self.writer.writeLine('')
		self.assertEqual(self.recorder.readline(), '')
		with self.assertRaises(NoMoreLinesToRead):
			self.recorder.readline()


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
				line.rstrip(kNewlineChar) for line in file.readlines())
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
		self.writer.increaseIndent()
		self.writer.writeLine('indented')
		self.writer.decreaseIndent()
		self.writer.writeLine('unindented')
		self.assertEqual(self.recorder.numberOfUnreadLines(), 3)
		self.assertEqual(self.recorder.readline(), 'unindented')
		self.assertEqual(self.recorder.readline(), '    indented')
		self.assertEqual(self.recorder.readline(), 'unindented')

	def testWriteMultilayeredIndent(self):
		def writeLayers(indentAmount, maxIndent):
			self.writer.writeLine('level %d' % indentAmount)
			if indentAmount < maxIndent:
				self.writer.increaseIndent()
				writeLayers(indentAmount + 1, maxIndent)
				self.writer.decreaseIndent()
		writeLayers(0, 3)
		self.assertEqual(self.recorder.numberOfUnreadLines(), 4)
		for line in self.recorder:
			numberFromLine = int(line.strip(' ').split(' ')[1])
			self.assertEqual(
					line,
					'%slevel %d' % (
							' ' * kIndentWidth * numberFromLine, 
							numberFromLine))

	def testDoubleIndent(self):
		self.writer.increaseIndent(2)
		self.writer.writeLine('double indent!')
		self.writer.decreaseIndent(1)
		self.writer.writeLine('single indent!')
		self.writer.increaseIndent(2)
		self.writer.writeLine('triple indent!')
		self.writer.decreaseIndent(2)
		self.writer.writeLine('single indent!')
		self.writer.decreaseIndent(1)
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

	def testIgnoreIndent(self):
		def getIndent(line):
			if not line.startswith('    '):
				return 0
			return getIndent(line[4:]) + 1
		self.writer.increaseIndent()
		self.writer.writeLine('blah')
		self.writer.ignoreIndent()
		self.writer.writeLine('blah')
		self.writer.writeLine('blah')
		self.writer.heedIndent()
		self.writer.writeLine('blah')
		self.writer.increaseIndent()
		self.writer.writeLine('blah')
		self.writer.ignoreIndent()
		self.writer.writeLine('blah')
		self.assertEqual(
				[getIndent(line) for line in self.recorder.readlines()],
				[1, 0, 0, 1, 2, 0])

	def testHeedIndent(self):
		pass


if __name__ == '__main__':
	unittest.main()
