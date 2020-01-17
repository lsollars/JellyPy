import configparser
import json
import logging
import pathlib

from jellypy.tierup import lib
from jellypy.tierup import interface
from jellypy.pyCIPAPI.auth import AuthenticatedCIPAPISession
from jellypy.tierup.irtools import IRJIO, IRJson

logger = logging.getLogger(__name__)


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
        irjo = IRJIO.get(irid, irversion, sess)
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
    # TODO: Accept irjo to run so tierup can be passed multiple inputs.
    tierup = lib.TierUpRunner(irjo)
    records = tierup.run()
    return records

def main(config, irid, irversion, irjson, outdir):
    logger.info('App start.')
    
    irjo = set_irj_object(irjson, irid, irversion, config)
    if not irjson:
        logger.info(f'Saving IRJson to output directory.')
        IRJIO.save(irjo, outdir=outdir)

    logger.info(f'Running tierup.')
    records = run_tierup(irjo)
    
    logger.info(f'Writing results.')
    csv_writer = lib.TierUpCSVWriter(outfile=pathlib.Path(outdir, irjo.irid + ".tierup.csv"))
    summary_writer = lib.TierUpSummaryWriter(outfile=pathlib.Path(outdir, irjo.irid + ".tierup.summary"))
    for record in records: # Records is a generator exhausted in one loop.
        csv_writer.write(record)
        summary_writer.write(record)
    csv_writer.close_file()
    summary_writer.close_file()

    logger.info('App end.')

if __name__ == "__main__":
    interface.cli()
