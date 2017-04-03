Main
====

A main class is defined to ease the creation of command line applications. This class follows the process:

1. Create a parser using ``argparse.ArgumentParser`` for the application:

    a) Calling all ``add_arguments(parser)`` methods from all super classes, e.g: ``clinner.mixins.HealthCheckMixin``.
    b) Addding a subparser for each command with their specific arguments.

2. Parse arguments using the argument parser created previously.

3. Inject variables into environment calling all super classes methods whose name starts with ``inject_``.

4. Load settings module from **CLINNER_SETTINGS** environment variable. More details below.
