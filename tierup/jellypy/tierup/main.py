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

def main(irjo: IRJson):
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
    writer = lib.TierUpCSVWriter(outfile=outfile)
    for record in records:
        writer.write(record)
    writer.close_file()

if __name__ == "__main__":
    interface.cli()
