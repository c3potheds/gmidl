#!/usr/local/bin/python

import unittest

import gmidl_wrappers
import gmidl_script_components
import test_util


class ConstructorTest(test_util.BaseTest):

    def setUp(self):
        super(test_util.BaseTest, self).setUp()
        self.testInput = []

    def tearDown(self):
        for inputCase in self.testInput:
            className = inputCase['className']
            scriptName = className + '_create'
            propertyNames = [prop[0]
                    for prop in inputCase.get('properties', [])]
            propertyTypes = [prop[1]
                    for prop in inputCase.get('properties', [])]
            dependencyNames = [dep[0]
                    for dep in inputCase.get('dependencies', [])]
            dependencyTypes = [dep[1]
                    for dep in inputCase.get('dependencies', [])]

            self.expectations.expect(gmidl_wrappers.writeConstructor(
                    className, propertyNames, propertyTypes))
                .shouldContain(gmidl_script_components.writeScriptPrototype(
                        scriptName, propertyNames, propertyTypes))
                .shouldContain(gmidl_script_components.writeScriptHeader(
                        scriptName))
                .shouldContain(gmidl_script_components.writeArrayAllocator(
                        className, propertyNames, propertyTypes))
                .shouldContain(gmidl_script_components.writeDsMapAllocator(
                        className, propertyNames, propertyTypes))
                .shouldContain(
                        gmidl_script_components.writeInitializerArguments(
                                dependencyNames, dependencyTypes))
                .shouldContain('return newInstance;\n')
        super(test_util.BaseTest, self).tearDown()

    def testNoProperties(self):
        self.testInput = [
            {'className': 'Foo'},
            {'className': 'Bar'},
            {'className': 'I'},
            {'className': 'A' * 81}
        ]

    def testOneProperty(self):
        self.testInput = [
            {
                'className': 'Foo',
                'properties': [
                    ('bar', 'Bar'),
                ],
            },
            {
                'className': 'ArrayList',
                'properties': [
                    ('initialCapacity', 'real'),
                ],
            },
            {
                'className': 'Message',
                'properties': [
                    ('message', 'string'),
                ],
            },
        ]

    def testMultipleProperties(self):
        self.testInput = [
            {
                'className': 'Foo',
                'properties': [
                    ('bar', 'Bar'),
                    ('baz', 'Baz'),
                ],
            },
            {
                'className': 'CustomResizeArrayList',
                'properties': [
                    ('initialCapacity', 'real'),
                    ('resizeFactor', 'real'),
                ],
            },
            {
                'className': 'Message',
                'properties': [
                    ('priority', 'real'),
                    ('message', 'string'),
                ],
            },
        ]

    def testOneDependency(self):
        pass

    def testMultipleDependencies(self):
        pass

    def testPropertiesAndDependencies(self):
        pass

    def testDisparatePropertyNameTypeSize(self):
        pass

    def testDisparateDependencyNameTypeSize(self):
        pass


class SetterTest(test_util.BaseTest):

    def testRealSetter(self):
        pass

    def testStringSetter(self):
        pass

    def testGmidlTypeSetter(self):
        pass

    def testAnyTypeSetter(self):
        pass


class GetterTest(test_util.BaseTest):

    def testRealGetter(self):
        pass

    def testStringGetter(self):
        pass

    def testGmidlTypeGetter(self):
        pass

    def testAnyTypeGetter(self):
        pass


class ScriptWrapperTest(test_util.BaseTest):

    def testNoArgs(self):
        pass

    def testOneArg(self):
        pass

    def testMultipleArgs(self):
        pass

    def testNonVirtualNoArgs(self):
        pass

    def testNonVirtualOneArg(self):
        pass

    def testNonVirtualMultipleArgs(self):
        pass

    def testDescription(self):
        pass

    def testLongDescription(self):
        pass


class ImplBoilerplateTest(test_util.BaseTest):

    def testNoArgs(self):
        pass

    def testOneArg(self):
        pass

    def testMultipleArgs(self):
        pass

    def testMoreThanSixteenArgs(self):
        pass

    def testDescription(self):
        pass

    def testLongDescription(self):
        pass


if __name__ == '__main__':
    unittest.main()
