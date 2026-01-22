from . import __version__
from .extractor import (
        list_info_cubes,
        valid_cubes_ids,
        csv_to_dataframe,
        InvalidCubeIDError,
        SNBDataEngine
)


def main():
    """A basic Command Line Interface for fetching cube data from SNB.
    Command Line Interface

    usage: (venv) python -m src [-h] [-v] [-s] [--info] [--version] cubes [cubes ...]

    SNB Data Streamliner: Extract and structure SNB data cubes.

    positional arguments:
      cubes          The name of the SNB data cube (e.g., 'rentm')

    options:
      -h, --help     show this help message and exit
      -v, --verbose  Increase output verbosity
      -s, --save     Save the extracted data to the /data folder. If not set, processing stays in RAM.
      --info         Display all supported cubes Id with description.
      --version      Display the version number.

    SNB data portal: 'https://data.snb.ch/en'.


    Examples of usage:
    # Multiple downloads
    (venv) $ python -m src rendeiduebd sddssbs14710q contourisma ambeschkla -v    
    """
    class CallInfoCubesAction(argparse.Action):
        """Custom action which call the function to display the cubes information."""
        def __call__(self, parser, namespace, values, option_string=None):
            print(list_info_cubes())
            parser.exit()

    parser = argparse.ArgumentParser(
        description="SNB Data Streamliner: Extract and structure SNB data cubes.",
        epilog="SNB data portal: 'https://data.snb.ch/en'."
    )
    # Mandatory
    parser.add_argument("cubes", nargs='+', help="The name of the SNB data cube (e.g., 'devlandm')")
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
        '--info',
        nargs=0,
        action=CallInfoCubesAction,
        help="Display all supported cubes Id with description."
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
    # Configuration entry points
    v_level = 'v'*min(args.verbose, 2) or None
    # Check validity of cubes ids
    valid_cube_ids = valid_cubes_ids()
    for cube in args.cubes:
        if cube not in valid_cube_ids:
            raise InvalidCubeIDError(cube)

    if len(args.cubes) == 1:
        # Single download
        cube = args.cubes.pop()
        # Fetch the data
        if args.save:
            # Save the data first then load it from disk
            with SNBDataEngine(logging_verbosity=v_level) as snb:
                path = snb.download_to_file(cube, selection=None)
                df = csv_to_dataframe(path, skiprows=2)
                print(df.head())
        else:
            # In RAM creation of the DataFrame
            with SNBDataEngine(logging_verbosity=v_level) as snb:
                df = snb.download_to_dataframe(cube, selection=None)
                if df is not None:
                    print(df.head())
    else:
        # Multiple sequential downloads (with sleep time)
        cubes = list(dict.fromkeys(args.cubes)) # remove duplicates
        with SNBDataEngine(logging_verbosity=v_level) as snb:
            paths = snb.download_to_files(cubes, selection=None)
            # Inspect the data cubes
            for i, path in enumerate(paths):
                df = csv_to_dataframe(path, skiprows=2)
                if df is not None:
                    print("Cube Id",cubes[i])
                    print(df.head())


if __name__ == "__main__":
    import argparse
    main()
