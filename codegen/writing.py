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

class LineWriter(object):

    def __init__(self, output=None, newline='\n'):
        self._output = output if output else sys.stdout
        self._newline = newline

    def writeLine(self, text=''):
        self._output.write(text + self._newline)


class IndentWriter(LineWriter):

    def __init__(self, writer=None, lineWriter=None, 
            indentWidth=4, indentChar=' '):
        self._indentPrefix = ''
        self._indentWidth = indentWidth
        self._writer = lineWriter if lineWriter else LineWriter(writer)
        self._heedIndent = True
        self._indentChar = indentChar

    def increaseIndent(self, amount=1):
        self._indentPrefix += (
                self._indentChar * self._indentWidth * amount)

    def decreaseIndent(self, amount=1):
        self._indentPrefix = self._indentPrefix[
                :-self._indentWidth * amount]

    def ignoreIndent(self):
        self._heedIndent = False

    def heedIndent(self):
        self._heedIndent = True

    def writeLine(self, text=''):
        if self._heedIndent:
            self._writer.writeLine(self._indentPrefix + text)
        else:
            self._writer.writeLine(text)


