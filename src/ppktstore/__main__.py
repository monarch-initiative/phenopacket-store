import argparse
import logging
import sys

import ppktstore


def main(argv) -> int:
    """
    Phenopacket-store CLI
    """
    parser = argparse.ArgumentParser(
        prog='ppktstore',
        formatter_class=argparse.RawTextHelpFormatter,
        description=main.__doc__,
    )
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=ppktstore.__version__))

    # generate subparsers/subcommands
    subparsers = parser.add_subparsers(dest='command')

    # #################### ------------- `package` ------------- ####################
    parser_package = subparsers.add_parser('package', help='Gather all phenopackets into a release archive')
    parser_package.add_argument(
        '--notebook-dir', default='notebooks',
        help='path to cohorts directory')
    parser_package.add_argument(
        '--output', required=False, default='phenopackets.zip',
        help='where to write the release archive')

    # #################### ------------- `qc` ------------------ ####################
    parser_check = subparsers.add_parser('qc', help='Q/C phenopackets')
    parser_check.add_argument(
        '--notebook-dir', default='notebooks',
        help='path to cohorts directory')
    
    # #################### ------------- `report` -------------- ####################
    report = subparsers.add_parser('report', help='Generate reports')
    subparsers_report = report.add_subparsers(dest='report_command')
    
    parser_collections = subparsers_report.add_parser('collections', help='Generate collections report')
    parser_collections.add_argument(
        '--notebook-dir', default='notebooks',
        help='path to cohorts directory')
    parser_collections.add_argument(
        '--notebook-dir-url', default='https://github.com/monarch-initiative/phenopacket-store/tree/main/notebooks',
        help='URL pointing to notebooks folder on GitHub')
    parser_collections.add_argument(
        '--output',
        help='where to generate the collections report')


    if len(argv) == 0:
        parser.print_help()
        return 1

    args = parser.parse_args(argv)
    setup_logging()

    logger = logging.getLogger(__name__)
    if args.command == 'package':
        return package_phenopackets(
            notebook_dir=args.notebook_dir,
            output=args.output,
            logger=logger,
        )
    elif args.command == 'qc':
        return qc_phenopackets(
            notebook_dir=args.notebook_dir,
            logger=logger,
        )
    elif args.command == 'report':
        if args.report_command == 'collections':
            return generate_collections_report(
                notebook_dir=args.notebook_dir,
                notebook_dir_url=args.notebook_dir_url,
                output=args.output,
                logger=logger,
            )
        else:
            report.print_help()
            return 1
    else:
        parser.print_help()
        return 1


def package_phenopackets(
        notebook_dir: str,
        output: str,
        logger: logging.Logger,
) -> int:
    phenopacket_store = read_phenopacket_store(notebook_dir, logger)
    archiver = ppktstore.archive.PhenopacketStoreArchiver(phenopacket_store=phenopacket_store)

    logger.info('Storing the phenopacket archive at %s', output)
    # Strip the `.zip` suffix if present
    outfilename = output
    suffix = '.zip'
    if outfilename.endswith(suffix):
        outfilename = outfilename[:-len(suffix)]
    archiver.get_store_zip(outfilename=outfilename)

    logger.info('Done!')
    return 0


def qc_phenopackets(
    notebook_dir: str,
    logger: logging.Logger,
) -> int:
    phenopacket_store = read_phenopacket_store(notebook_dir, logger)
    logger.info('Checking phenopackets')
    checker = ppktstore.qc.configure_qc_checker()
    results = checker.check(phenopacket_store=phenopacket_store)
    if results.is_ok():
        logger.info('No Q/C issues were found')
        return 0
    else:
        logger.info('Phenopacket store Q/C failed')
        
        for checker_name, issues in results.iter_results():
            logger.info('\'%s\' found %d error(s):', checker_name, len(issues))
            for error in issues:
                logger.info(' - %s', error)
        return 1


def read_phenopacket_store(
    notebook_dir: str, 
    logger: logging.Logger,
) -> ppktstore.model.PhenopacketStore:
    logger.info('Reading phenopackets at `%s`', notebook_dir)
    phenopacket_store = ppktstore.model.PhenopacketStore.from_notebook_dir(notebook_dir)
    logger.info(
        'Read %d cohorts with %d phenopackets', 
        phenopacket_store.cohort_count(), 
        phenopacket_store.phenopacket_count(),
    )
    return phenopacket_store


def generate_collections_report(
        notebook_dir: str,
        notebook_dir_url: str,
        output: str,
        logger: logging.Logger,
) -> int:
    logger.info('Generating report for phenopackets at %s', notebook_dir)
    logger.info('Using notebook URL `%s`', notebook_dir_url)
    report = ppktstore.stats.generate_phenopacket_store_report(
        notebook_dir=notebook_dir,
        notebook_dir_url=notebook_dir_url,
    )

    logger.info('Writing report to %s', output)
    with open(output, 'w') as fh:
        fh.write(report)

    logger.info('Done!')
    return 0


def setup_logging():
    level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter
    formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-3s : %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
