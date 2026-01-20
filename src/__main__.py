from . import __version__
from . import SNBDataEngine


def main():
    """A basic Command Line Interface for fetching datasets (cubes) from SNB."""
    parser = argparse.ArgumentParser(        
        description="SNB Data Streamliner: Extract and structure SNB data cubes.",
        epilog="SNB data portal: 'https://data.snb.ch/en'."
    )
    # Mandatory
    parser.add_argument("cube", help="The name of the SNB data cube (e.g., 'rentm')")
    # Optional
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase output verbosity")
    # Optional: if true save to disk
    parser.add_argument(
        "-s", "--save", 
        action="store_true", 
        help="Save the extracted data to the /data folder. If not set, processing stays in RAM."
    )
    # Optional
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"%(prog)s {__version__}",
        help="Display the version number."
    )

    # Parse the command line options, i.e. args.argv
    args = parser.parse_args()
    # Initialize the entry points
    cube = args.cube
    v_level = 'v'*min(args.verbose, 2) or None

    # Fetch the data
    if args.save:
        with SNBDataEngine(logging_verbosity=v_level) as snb:
            path = snb.download_to_file(cube, selection="balsiscrevol")
            file_path = Path(path)
            if file_path.exists() and file_path.is_file():
                df = pd.read_csv(file_path, sep=';', skiprows=2, parse_dates=True)
                print(df.head())
    else:
        with SNBDataEngine(logging_verbosity=v_level) as snb:
            df = snb.download_to_dataframe(cube, selection="balsiscrevol")
            if df is not None:
                print(df.head())


if __name__ == "__main__":
    import argparse
    main()
