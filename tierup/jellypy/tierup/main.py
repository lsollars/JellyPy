import configparser
import json
import pathlib

from jellypy.tierup import lib
from jellypy.tierup import interface
from jellypy.pyCIPAPI.auth import AuthenticatedCIPAPISession
from jellypy.tierup.irtools import IRJIO


def main(irjo, outdir=None):   
    # Add any updated panel app panels
    lib.PanelUpdater().add_event_panels(irjo)
    
    # Run Tierup on T3 variants in irjo
    tierup = lib.TierUpRunner(irjo)
    tier_three_events = tierup.generate_events()
    records = tierup.run(tier_three_events)

    # Write records
    outdir = outdir or ''
    outfile = pathlib.Path(outdir, irjo.irid + '.tierup.csv')
    writer = lib.TierUpCSVWriter(outfile=outfile)
    for record in records:
        writer.write(record)
    writer.close_file()

if __name__ == "__main__":
    interface.cli()
