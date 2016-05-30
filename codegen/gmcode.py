#!/usr/local/bin/python

import writing

class CodeWriter(object):

    def __init__(self, writer=None):
        self._writer = writer if writer else writing.IndentWriter()


class GmCode(object):

    def writeCode(self, writer):
        pass


class Expression(GmCode):

    def __init__(self, text):
        self._text = text

    def writeCode(self, writer):
        writer.write(self._text)


class Statement(GmCode):

    def __init__(self, expression):
        self._expression = expression

    def writeCode(self, writer):
        self._expression.writeCode(writer)
        writer.writeLine(';')


class Comment(Statement):

    def __init__(self, text=None):
        self._text = ' %s' % text if text else ''

    def writeCode(self, writer):
        writer.writeLine('//%s' % self._text)


class ScriptPrototype(Statement):

    def __init__(self, functionName, arguments=None, returnType=None):
        self._functionName = functionName
        self._arguments = arguments if arguments else []
        if not returnType:
            self._returnType = ''
        else:
            prefix = '; -> ' if arguments else '-> '
            self._returnType = prefix + returnType

    def writeCode(self, writer):
        writer.writeLine(
                '///%s(%s%s)' % (
                        self._functionName,
                        ', '.join(self._arguments),
                        self._returnType))


class ScriptHeader(Statement):

    def __init__(self, text):
        self._text = text

    def writeCode(self, writer):
        asterisks = '*' * (writer.getRemainingSpaceInLine() - 1)
        writer.writeLine('/' + asterisks)
        writer.writeLine(self._text)
        writer.writeLine(asterisks + '/')


class FunctionCall(Expression):

    def __init__(self, functionName, arguments=None):
        self._functionName = functionName
        self._arguments = arguments if arguments else []

    def writeCode(self, writer):
        writer.write('%s(' % self._functionName)
        if len(self._arguments):
            for argument in self._arguments[:-1]:
                argument.writeCode(writer)
                writer.write(', ')
            self._arguments[-1].writeCode(writer)
        writer.write(')')


class BinaryOperation(Expression):

    kValidOperators = ['+', '-', '*', '/', '%', 'div', 'mod']

    def __init__(self, leftOperand, operator, rightOperand):
        assert operator in self.kValidOperators
        assert isinstance(leftOperand, Expression)
        assert isinstance(rightOperand, Expression)
        self._leftOperand = leftOperand
        self._operator = operator
        self._rightOperand = rightOperand

    def writeCode(self, writer):
        self._leftOperand.writeCode(writer)
        writer.write(' %s ' % self._operator)
        self._rightOperand.writeCode(writer)



class IfClause(GmCode):

    def __init__(self, condition, body):
        assert isinstance(condition, Expression)
        assert isinstance(body, Statement)
        self._condition = condition
        self._body = body

    def writeCode(self, writer):
        writer.write('if (')
        self._condition.writeCode(writer)
        writer.writeLine(') {')
        with writer.indent():
            self._body.writeCode(writer)
        writer.write('}')


class ElseIfClause(GmCode):

    def __init__(self, condition, body):
        assert isinstance(condition, Expression)
        assert isinstance(body, Statement)
        self._condition = condition
        self._body = body

    def writeCode(self, writer):
        writer.write(' else if (')
        self._condition.writeCode(writer)
        writer.writeLine(') {')
        with writer.indent():
            self._body.writeCode(writer)
        writer.write('}')


class IfStatement(Statement):

    def __init__(self, ifClause, *elseClauses):
        assert isinstance(ifClause, IfClause)
        assert all(
                isinstance(clause, ElseIfClause)
                for clause in elseClauses[:-1])
        assert (len(elseClauses) == 0
                or isinstance(elseClauses[-1], ElseIfClause)
                or isinstance(elseClauses[-1], Statement))
        self._ifClause = ifClause
        if len(elseClauses) > 0:
            if isinstance(elseClauses[-1], ElseIfClause):
                self._elseIfClauses = elseClauses[:]
                self._elseClause = None
            else:
                self._elseIfClauses = elseClauses[:-1]
                self._elseClause = elseClauses[-1]
        else:
            self._elseIfClauses = []
            self._elseClause = None

    def writeCode(self, writer):
        self._ifClause.writeCode(writer)
        for elseClause in self._elseIfClauses:
            elseClause.writeCode(writer)
        if self._elseClause:
            writer.writeLine(' else {')
            with writer.indent():
                self._elseClause.writeCode(writer)
            writer.writeLine('}')
        else:
            writer.writeLine('')


class ForLoop(Statement):

    def __init__(self, initializerExpression, conditionExpression,
            updateExpression, body):
        assert all(
                isinstance(e, Expression)
                for e in [
                    initializerExpression,
                    conditionExpression,
                    updateExpression])
        assert isinstance(body, Statement)
        self._initializerExpression = initializerExpression
        self._conditionExpression = conditionExpression
        self._updateExpression = updateExpression
        self._body = body

    def writeCode(self, writer):
        writer.write('for (')
        self._initializerExpression.writeCode(writer)
        writer.write('; ')
        self._conditionExpression.writeCode(writer)
        writer.write('; ')
        self._updateExpression.writeCode(writer)
        writer.writeLine(') {')
        with writer.indent():
            self._body.writeCode(writer)
        writer.writeLine('}')


class VariableAssignment(Expression):

    def __init__(self, varName, expression=None, declaration=True):
        if expression:
            assert isinstance(expression, Expression)
        self._varName = varName
        self._expression = expression
        self._declaration = declaration

    def writeCode(self, writer):
        if self._declaration:
            writer.write('var ')
        writer.write(self._varName)
        if self._expression:
            writer.write(' = ')
            self._expression.writeCode(writer)


class Statements(Statement):

    def __init__(self, statements):
        assert all(
                isinstance(statement, Statement)
                for statement in statements)
        self._statements = list(statements)

    def writeCode(self, writer):
        for statement in self._statements:
            statement.writeCode(writer)


