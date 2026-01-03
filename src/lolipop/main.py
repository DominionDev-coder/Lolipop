"""
Lolipop entrypoint

The entrypoint to lolipop utility.
Receives commands, uses handlers for self and global arguments.
"""

import typer
from lolipop.commands.init import app as init_app
from lolipop.commands.run import app as run_app
from lolipop.commands.project import app as project_app


app = typer.Typer(help="🍭 Lolipop: A developer utility for installing, setting up, and managing projects and environments effortlessly.", no_args_is_help=True)

# Register commands
app.add_typer(init_app, name="init")
app.add_typer(run_app, name="run")
app.add_typer(project_app, name="project")



def main():
    """
    Main entrypoint for the CLI.
    """
    app()


if __name__ == "__main__":
    main()
