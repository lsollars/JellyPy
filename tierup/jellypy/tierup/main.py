import configparser
import json
import logging
import pathlib

from jellypy.tierup.logger import log_setup
from jellypy.tierup import lib
from jellypy.tierup import interface
from jellypy.pyCIPAPI.auth import AuthenticatedCIPAPISession
from jellypy.tierup.irtools import IRJIO, IRJson

logger = logging.getLogger(__name__)

def main(config, irid, irversion, irjson, outdir):
    logger.info('App start')
    irjo = set_irj_object(irjson, irid, irversion, config)
    records = run_tierup(irjo)
    outfile = pathlib.Path(outdir or "", irjo.irid + ".tierup.csv")
    write_csv(records, outfile)
    logger.info('App end')

def set_irj_object(irjson, irid, irversion, config):
    if irjson:
        logger.info(f'Reading from local file: {irjson}')
        irjo = IRJIO.read(irjson)
    elif irid and irversion:
        logger.info(f'Downloading from CIPAPI: {irid}-{irversion}')
        sess = AuthenticatedCIPAPISession(
            auth_credentials={
                'username': config.get('pyCIPAPI', 'username'),
                'password': config.get('pyCIPAPI', 'password')
            }
        )
        irjio = IRJIO.get(irid, irversion, sess)
    else:
        raise Exception('Invalid argument')
    return irjo

def run_tierup(irjo: IRJson):
    # IRJ contains panels as they are named today but report events contain legacy panel names.
    #    Search for panel name mismatches and add under the relevant panel ID today.
    logger.info('Searching for merged PanelApp panels')
    lib.PanelUpdater().add_event_panels(irjo)

    logger.info(f'Running TierUp for {irjo}')
    # Run Tierup on T3 variants in irjo
    tierup = lib.TierUpRunner(irjo)
    records = tierup.run()
    return records

def write_csv(records, outfile):
    logger.info(f'Writing results to {outfile}')
    writer = lib.TierUpCSVWriter(schema=lib.report_schema, outfile=outfile)
    for record in records:
        writer.write(record)
    writer.close_file()

if __name__ == "__main__":
    interface.cli()
