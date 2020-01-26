import click
import configparser
import json
import logging
import pathlib

from jellypy.tierup.irtools import IRJIO
from jellypy.tierup.main import main
from jellypy.tierup.logger import log_setup


log_setup()
logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def parse_config(ctx, param, value):
    """Click callback to return config.ini as dictionary."""
    config = configparser.ConfigParser()
    config.read(value)
    return config

@click.command()
@click.option(
    "-c", "--config", type=click.Path(exists=True), callback=parse_config,
    help="A jellypy.tierup config file path", required=True
)
@click.option(
    "-i", "--irid", type=click.INT, help="GeL interpretation request ID. E.g. 1234"
)
@click.option(
    "-iv", "--irversion", type=click.INT, help="GeL interpretation request version. E.g. 1"
)
@click.option(
    "-j", "--irjson", type=click.Path(exists=True), help="GeL interpretation request json file. E.g. data/1234.json"
)
@click.option(
    "-o", "--outdir", type=click.Path(), help="Output directory for tierup files", default=""
)
def cli(config, irid, irversion, irjson, outdir):
    """Command line interface."""
    logger.info(f'CLI args: {config}, {irid}, {irversion}, {irjson}, {outdir}')
    main(config, irid, irversion, irjson, outdir)

