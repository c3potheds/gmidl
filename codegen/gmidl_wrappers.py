#!/usr/local/bin/python


import gmidl_script_components


_kConstructorTemplate = """
%(prototype)s
%(header)s

var %(instanceName)s;

if (GMIDL_CLASS_STYLE == GMIDL_CLASS_STYLE_ARRAY) {
    %(arrayAllocator)s
} else if (GMIDL_CLASS_STYLE == GMIDL_CLASS_STYLE_DSMAP) {
    %(dsMapAllocator)s
}

%(argumentDeclarations)s

__IMPL_%(className)s_create(%(instanceName)s, argv);

return %(instanceName)s;
""".lstrip('\n')
def writeConstructor(className, propertyNames=None, propertyTypes=None,
        dependencyNames=None, dependencyTypes=None):
    return _kConstructorTemplate % {
        'className': className,
        'prototype': writeScriptPrototype(),
        'header': gmidl_script_components.writeScriptHeader(),
        'arrayAllocator': gmidl_script_components.writeArrayAllocator(),
        'dsMapAllocator': gmidl_script_components.writeDsMapAllocator(),
        'argumentDeclarations': writeInitializerArguments(),
    }


_kSetterTemplate = """
%(prototype)s
%(header)s
%(notice)s

var self = argument0;
var value = argument1;
if (GMIDL_ENFORCE_TYPES) {
    __check_instanceof__(self, %(className)s);
    __check_instanceof__(value, %(propertyType)s);
}

if (GMIDL_CLASS_STYLE == GMIDL_CLASS_STYLE_ARRAY) {
    self[@__%(className)s_properties_%(propertyName)s] = value;
} else if (GMIDL_CLASS_STYLE == GMIDL_CLASS_STYLE_DSMAP) {
    ds_map_set(self, __%(className)s_properties_%(propertyName)s, value);
""".lstrip('\n')
def writeSetter(className, propertyName, propertyType):
    return _kSetterTemplate % {
        'prototype': gmidl_script_components.writeScriptPrototype(
                '%s_set%s' % (className, propertyName),
                ['self', propertyName],
                ['', propertyType]),
        'header': gmidl_script_components.writeScriptHeader(
            scriptName,
            'Sets the value of %s for a %s' % (propertyName, className))
        'className': className,
        'propertyName': propertyName,
        'propertyType': propertyType,
    }


_kGetterTemplate = """
%(prototype)s
%(header)s
%(notice)s

var %(instanceName)s = argument0;

if (GMIDL_CLASS_STYLE == GMIDL_CLASS_STYLE_ARRAY) {
    return %(instanceName)s[__%(className)s_properties_%(propertyName)s];
} else if (GMIDL_CLASS_STYLE == GMIDL_CLASS_STYLE_DSMAP) {
    return %(instanceName)s[? __%(className)s_properties_%(propertyName)s];
} else {
    NOTREACHED('GMIDL_CLASS_STYLE is an invalid value: %d', GMIDL_CLASS_STYLE);
}
""".lstrip('\n')
def writeGetter(className, propertyName, propertyType):
    scriptName = '%s_set%s' % (className, propertyName)
    return _kGetterTemplate % {
        'prototype': gmidl_script_components.writeScriptPrototype(
                scriptName,
                ['self', propertyName],
                ['', propertyType]),
        'header': gmidl_script_components.writeScriptHeader(
                scriptName,
                'Gets the value for %s from a %s' % (propertyName, className)),
        'notice': gmidl_script_components.kDoNotEditNotice,
        'className': className,
        'propertyName': propertyName,
        'instanceName': 'self'
    }


_kScriptWrapperTemplate = """
%(prototype)s
%(scriptHeader)s
%(notice)s

if (GMIDL_PROFILE_TIME) {
    // If time profiling is on, get the time that the script started running.
    __profile_time_push__(%(scriptName)s);
}

// Arguments are passed as an array to the implementation script.
var %(argv)s;
%(variableDeclarations)s

if (GMIDL_TRACK_SCOPE) {
    __push_scope__(%(scriptName)s, %(argv)s);
}

// Call the script implementation
var returnValue = %(implCall)s;

if (GMIDL_TRACK_SCOPE) {
    __pop_scope__();
}

// Free the argument array
%(argv)s = 0;

if (GMIDL_PROFILE_TIME) {
    // If time profiling is on, get the time that the script scope exited.
    // The difference between the start and end times is then logged.
    __profile_time_pop__();
}

return returnValue;
""".lstrip('\n')
def writeScriptWrapper(
        scriptName,
        argNames=None,
        argTypes=None,
        returnType=None,
        description='',
        longDescription='',
        returnDescription='',
        virtual=True):
    argv = 'argv'
    return _scriptWrapperTemplate % {
        'scriptName': scriptName,
        'prototype': writeScriptPrototype(
                scriptName, argNames, argTypes, returnType),
        'notice': gmidl_script_components.kDoNotEditNotice,
        'scriptHeader': gmidl_script_components.writeScriptHeader(
                scriptName, description, longDescription, returnDescription),
        'variableDeclarations': writeVariableDeclarations(
                argv, argNames, argTypes),
        'implCall': _writeImplCall(virtual),
        'argv': argv,
    }


_kImplTemplate = """
%(header)s

%(declarations)s

%(notice)s

""".lstrip('\n')
def writeImplBoilerplate(methodName, argNames, description='',
        longDescription=''):
    return _kImplTemplate % {
        'header': gmidl_script_components.writeScriptHeader(methodName, description, longDescription),
        'declarations': writeImplVariableDeclarations(argNames),
        'notice': gmidl_script_components.kImplScriptNotice,
    }

