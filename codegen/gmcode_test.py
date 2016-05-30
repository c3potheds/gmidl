#!/usr/local/bin/python

import itertools
import unittest

import gmcode
import writing

class Recorder(object):

    def __init__(self):
        self._recordedText = ''

    def write(self, text):
        self._recordedText += text

    def readAll(self):
        return self._recordedText

    def reset(self):
        self._recordedText = ''


class CodeWritingTest(unittest.TestCase):

    def setUp(self):
        self.recorder = Recorder()
        self.writer = writing.IndentWriter(self.recorder)
        self.expectedResults = []
        self.fixtures = []

    def tearDown(self):
        self.assertEqual(len(self.expectedResults), len(self.fixtures))
        for fixture, expectedResult in zip(
                self.fixtures, self.expectedResults):
            fixture.writeCode(self.writer)
            self.assertEqual(self.recorder.readAll(), expectedResult)
            self.recorder.reset()

    def testWriteComment(self):
        self.expectedResults += [
            '// This is a comment.\n',
            '//\n',
            '//\n',
        ]
        self.fixtures += [
            gmcode.Comment('This is a comment.'),
            gmcode.Comment(),
            gmcode.Comment(''),
        ]

    def testWriteScriptPrototype(self):
        self.expectedResults += [
            '///DoABarrelRoll()\n',
            '///TakeAHike(self, boots Boots, backpack Backpack; '
                    + '-> PhotoAlbum)\n',
            '///TryASomersault(-> bool)\n',
            '///Eat(food Food)\n',
            '///Drink(drink Liquid)\n',
            '///BeMerry()\n'
        ]
        self.fixtures += [
            gmcode.ScriptPrototype('DoABarrelRoll'),
            gmcode.ScriptPrototype(
                    'TakeAHike',
                    ['self', 'boots Boots', 'backpack Backpack'],
                    'PhotoAlbum'),
            gmcode.ScriptPrototype('TryASomersault', returnType='bool'),
            gmcode.ScriptPrototype('Eat', ['food Food']),
            gmcode.ScriptPrototype('Drink', ['drink Liquid'], None),
            gmcode.ScriptPrototype('BeMerry', [], None),
        ]

    def testWriteScriptHeader(self):
        self.expectedResults += [r.lstrip('\n') for r in [
"""
/*******************************************************************************
Look at me!
*******************************************************************************/
""",
"""
/*******************************************************************************
First line.
Second line.
*******************************************************************************/
""",
"""
/*******************************************************************************
Space below this line.

The above line was skipped.
*******************************************************************************/
""",
]]
        self.fixtures += [
            gmcode.ScriptHeader('Look at me!'),
            gmcode.ScriptHeader('First line.\nSecond line.'),
            gmcode.ScriptHeader(
                    'Space below this line.\n\nThe above line was skipped.')
        ]

    def testWriteFunctionCall(self):
        self.expectedResults += [
            'ds_map_create()',
            'BarrelRoll(times)',
            'DoWhatever(foo, bar, baz)',
            'abs(angle1 + angle2)',
            'fun(this - that, which + watch)',
        ]
        self.fixtures += [
            gmcode.FunctionCall('ds_map_create'),
            gmcode.FunctionCall('BarrelRoll', [
                gmcode.Expression('times')
            ]),
            gmcode.FunctionCall('DoWhatever', [
                gmcode.Expression('foo'),
                gmcode.Expression('bar'),
                gmcode.Expression('baz'),
            ]),
            gmcode.FunctionCall('abs', [
                gmcode.BinaryOperation(
                        gmcode.Expression('angle1'),
                        '+',
                        gmcode.Expression('angle2')),
            ]),
            gmcode.FunctionCall('fun', [
                gmcode.BinaryOperation(
                        gmcode.Expression('this'),
                        '-',
                        gmcode.Expression('that')),
                gmcode.BinaryOperation(
                        gmcode.Expression('which'),
                        '+',
                        gmcode.Expression('watch')),
            ]),

        ]

    def testWriteBinaryOperation(self):
        self.expectedResults += [
            '1 + 1',
            'whatever * 3',
            'something div somethingElse',
        ]
        self.fixtures += [
            gmcode.BinaryOperation(
                    gmcode.Expression('1'),
                    '+',
                    gmcode.Expression('1')),
            gmcode.BinaryOperation(
                    gmcode.Expression('whatever'),
                    '*',
                    gmcode.Expression('3')),
            gmcode.BinaryOperation(
                    gmcode.Expression('something'),
                    'div',
                    gmcode.Expression('somethingElse')),
        ]

    def testWriteCustomExpression(self):
        self.expectedResults += [
            'objectName',
            '"String"',
            "'String'",
            'CONSTANT_CALL',
        ]
        self.fixtures += [
            gmcode.Expression('objectName'),
            gmcode.Expression('"String"'),
            gmcode.Expression("'String'"),
            gmcode.Expression('CONSTANT_CALL'),
        ]

    def testWriteStatement(self):
        self.expectedResults += [
            'DoABarrelRoll();\n',
            'GetObjectRef().varName;\n',
            'outerfunction(innerfunction());\n',
            'one(two(), three(four()));\n',
        ]
        self.fixtures += [
            gmcode.Statement(gmcode.FunctionCall('DoABarrelRoll')),
            gmcode.Statement(gmcode.Expression('GetObjectRef().varName')),
            gmcode.Statement(gmcode.FunctionCall('outerfunction', [
                gmcode.FunctionCall('innerfunction'),
            ])),
            gmcode.Statement(gmcode.FunctionCall('one', [
                gmcode.FunctionCall('two'),
                gmcode.FunctionCall('three', [
                    gmcode.Expression('four()'),
                ]),
            ])),
        ]

    def testWriteIfStatement(self):
        self.expectedResults += [
            'if (varName) {\n    show_message("hi");\n}\n',
            'if (i > 0) {\n    gotofail();\n    dothings();\n}\n',
            'if (true) {\n    a();\n} else {\n    b();\n}\n',
            'if (false) {\n    a();\n} else if (true) {\n    b();\n}\n',
            'if (n) {\n    a();\n} '
                    + 'else if (m) {\n    b();\n} else {\n    c();\n}\n',
        ]
        self.fixtures += [
            gmcode.IfStatement(
                gmcode.IfClause(
                    gmcode.Expression('varName'),
                    gmcode.Statement(gmcode.Expression('show_message("hi")')))),
            gmcode.IfStatement(
                gmcode.IfClause(
                    gmcode.Expression('i > 0'),
                    gmcode.Statements([
                        gmcode.Statement(gmcode.FunctionCall('gotofail')),
                        gmcode.Statement(gmcode.FunctionCall('dothings')),
                    ]))),
            gmcode.IfStatement(
                gmcode.IfClause(
                    gmcode.Expression('true'),
                    gmcode.Statement(gmcode.FunctionCall('a'))),
                gmcode.Statement(gmcode.FunctionCall('b'))),
            gmcode.IfStatement(
                gmcode.IfClause(
                    gmcode.Expression('false'),
                    gmcode.Statement(gmcode.FunctionCall('a'))),
                gmcode.ElseIfClause(
                    gmcode.Expression('true'),
                    gmcode.Statement(gmcode.FunctionCall('b')))),
            gmcode.IfStatement(
                gmcode.IfClause(
                    gmcode.Expression('n'),
                    gmcode.Statement(gmcode.FunctionCall('a'))),
                gmcode.ElseIfClause(
                    gmcode.Expression('m'),
                    gmcode.Statement(gmcode.FunctionCall('b'))),
                gmcode.Statement(gmcode.FunctionCall('c'))),
        ]

    def testWriteForLoop(self):
        self.expectedResults += [
            'for (var i = 0; i < ds_list_size(list); i++) {'
                    + '\n    var item = ds_list_find_value(list, i);'
                    + '\n    Item_doThing(item);\n}\n',
            'for (var item = Begin(list); item != undefined; item = Next()) {'
                    + '\n    Item_doThing(item);\n}\n',
        ]
        self.fixtures += [
            gmcode.ForLoop(
                gmcode.VariableAssignment('i', gmcode.Expression('0')),
                gmcode.Expression('i < ds_list_size(list)'),
                gmcode.Expression('i++'),
                gmcode.Statements([
                    gmcode.Statement(
                        gmcode.VariableAssignment('item',
                            gmcode.FunctionCall('ds_list_find_value', [
                                gmcode.Expression('list'),
                                gmcode.Expression('i'),
                            ]))),
                    gmcode.Statement(
                        gmcode.FunctionCall('Item_doThing', [
                            gmcode.Expression('item')
                        ]))])),
            gmcode.ForLoop(
                gmcode.VariableAssignment('item',
                    gmcode.FunctionCall('Begin', [
                        gmcode.Expression('list')
                    ])),
                gmcode.Expression('item != undefined'),
                gmcode.VariableAssignment('item',
                    gmcode.FunctionCall('Next'), False),
                gmcode.Statements([
                    gmcode.Statement(
                        gmcode.FunctionCall('Item_doThing', [
                            gmcode.Expression('item')
                        ]))])),
        ]

    def testWriteVariableAssignment(self):
        self.expectedResults += [
            'var i = 0',
            'i = ds_list_create()',
            'var foo = Bar(Baz())',
        ]
        self.fixtures += [
            gmcode.VariableAssignment('i', gmcode.Expression('0')),
            gmcode.VariableAssignment('i',
                gmcode.FunctionCall('ds_list_create'), False),
            gmcode.VariableAssignment('foo',
                gmcode.FunctionCall('Bar', [gmcode.FunctionCall('Baz')])),
        ]

    def testWriteManyStatements(self):
        self.expectedResults += [
            'Foo();\nBar();\nBaz();\n',
        ]
        self.fixtures += [
            gmcode.Statements([
                gmcode.Statement(gmcode.FunctionCall('Foo')),
                gmcode.Statement(gmcode.FunctionCall('Bar')),
                gmcode.Statement(gmcode.FunctionCall('Baz'))
            ]),
        ]


if __name__ == '__main__':
    unittest.main()

