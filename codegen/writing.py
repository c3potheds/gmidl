#!/usr/local/bin/python

"""A module for writing formatted text with newlines and indentation.

All text that you want to format with indentation should pass through an
IndentWriter object, which has the methods increaseIndent(),
decreaseIndent(), ignoreIndent(), and heedIndent() to easily interact with
the states. For example:

    import codegen.writing

    writer = codegen.writing.IndentWriter(codegen.writing.LineWriter)
    writer.writeLine('Dear Bob,')
    writer.increaseIndent()
    writer.writeLine()
    writer.writeLine('How are you?')
    writer.decreaseIndent()
    writer.writeLine()
    writer.writeLine('Sincerely, Frank')

will print the following:

>>Dear Bob,
>>
>>    How are you?
>>
>>Sincerely, Frank

This is meant to be used by code-generating utilities to produce
well-formatted code.

The IndentWriter extends LineWriter, which takes any object with
a write() method with one argument, including Python file-like objects.

To test, run:

  python writing_test.py
"""

import sys


kDefaultIndentWidth = 4
kDefaultIndentChar = ' '
kDefaultMaxLineWidth = 80
kDefaultNewlineChar = '\n'


class LineWriter(object):

    def __init__(self, output=None, newline=kDefaultNewlineChar):
        self._output = output if output else sys.stdout
        self._newline = newline

    def write(self, text):
        self._output.write(text)

    def writeLine(self, text=''):
        self._output.write(text + self._newline)


class IndentWriter(LineWriter):

    class _Indent(object):

        def __init__(self, indentWriter, amount):
            self._indentWriter = indentWriter
            self._amount = amount

        def __enter__(self):
            self._indentWriter._increaseIndent(self._amount)

        def __exit__(self, exceptionType, exception, traceback):
            self._indentWriter._decreaseIndent(self._amount)


    class _IgnoreIndent(object):

        def __init__(self, indentWriter):
            self._indentWriter = indentWriter
            self._previousValue = None

        def __enter__(self):
            self._previousValue = self._indentWriter._heedIndent
            self._indentWriter._heedIndent = False

        def __exit__(self, exceptionType, exception, traceback):
            self._indentWriter._heedIndent = self._previousValue


    def __init__(self, writer=None, lineWriter=None,
            indentWidth=kDefaultIndentWidth,
            indentChar=kDefaultIndentChar,
            maxLineWidth=kDefaultMaxLineWidth):
        self._indentPrefix = ''
        self._indentWidth = indentWidth
        self._writer = lineWriter if lineWriter else LineWriter(writer)
        self._heedIndent = True
        self._indentChar = indentChar
        self._maxLineWidth = maxLineWidth
        self._atLineStart = True

    def indent(self, amount=1):
        return self._Indent(self, amount)

    def _increaseIndent(self, amount=1):
        self._indentPrefix += (
                self._indentChar * self._indentWidth * amount)

    def _decreaseIndent(self, amount=1):
        self._indentPrefix = self._indentPrefix[
                :-self._indentWidth * amount]

    def ignoreIndent(self):
        return self._IgnoreIndent(self)

    def write(self, text):
        if self._heedIndent and self._atLineStart:
            self._writer.write(self._indentPrefix + text)
        else:
            self._writer.write(text)
        self._atLineStart = False

    def writeLine(self, text=''):
        if self._heedIndent and self._atLineStart:
            self._writer.writeLine(self._indentPrefix + text)
        else:
            self._writer.writeLine(text)
        self._atLineStart = True

    def getRemainingSpaceInLine(self):
        return self._maxLineWidth - len(self._indentPrefix)


