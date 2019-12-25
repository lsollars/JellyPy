import click
import configparser
import json
import logging
import pathlib

from jellypy.tierup.irtools import IRJIO
from jellypy.tierup.main import main, write_csv
from jellypy.tierup.logger import log_setup

import jellypy.tierup.lib as tulib

log_setup()
logger = logging.getLogger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def parse_config(ctx, param, value):
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
    "-o", "--outdir", type=click.Path(), help="Output directory for tierup files", default=None
)
def cli(config, irid, irversion, irjson, outdir):
    logger.info('App start')
    irjo = tulib.set_irj_object(irjson, irid, irversion, config)
    records = main(irjo)
    outfile = pathlib.Path(outdir or "", irjo.irid + ".tierup.csv")
    write_csv(records, outfile)
    logger.info('App end')
