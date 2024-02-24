"""
Run customized Flask app locally (i.e., with Flask development server).

Author: Nikolay Lysenko
"""


import argparse
import json

from readingbricks import app
from readingbricks.resources import make_resources


def parse_cli_args() -> argparse.Namespace:
    """
    Parse arguments passed via Command Line Interface (CLI).

    :return:
        namespace with arguments
    """
    parser = argparse.ArgumentParser(description='Flask app for reading and searching notes')
    parser.add_argument(
        '-c', '--config_path', type=str, default=None, help='path to configuration file'
    )
    cli_args = parser.parse_args()
    return cli_args


def main() -> None:
    """Parse CLI arguments and run app locally."""
    cli_args = parse_cli_args()
    if cli_args.config_path is not None:
        app.config.from_file(cli_args.config_path, load=json.load)
    make_resources(
        app.config.get("NOTES_DIR"), app.config.get("RESOURCES_DIR"), app.config.get('LANGUAGE')
    )
    app.run(debug=True)


if __name__ == '__main__':
    main()
