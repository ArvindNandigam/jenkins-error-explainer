# error_taxonomy.py

ERROR_CATEGORIES = {
    # Groovy / pipeline syntax
    "groovy_syntax_error": [
        r"MultipleCompilationErrorsException",
        r"expecting '\}'",
        r"WorkflowScript"
    ],

    # Agent / executor issues
    "missing_agent": [
        r"requires a node context",
        r"agent none"
    ],

    "no_node_available": [
        r"There are no nodes with the label",
        r"doesn’t have label",
        r"does not have label",
        r"Still waiting to schedule task"
    ],

    # SCM / Git related
    "git_authentication_error": [
        r"Authentication failed",
        r"Invalid username or token",
        r"Error cloning remote repo"
    ],

    # Jenkins credentials system
    "missing_credentials": [
        r"Credentials .* not found",
        r"Could not find credentials entry with ID"
    ],

    # Plugin / DSL
    "missing_plugin": [
        r"No such DSL method",
        r"No such step"
    ],

    # File system
    "file_not_found": [
        r"No such file or directory",
        r"cannot open",
        r"script returned exit code 1"
    ]
}
