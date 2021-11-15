import argparse
from pathlib import Path

import mediaprobe
from mediaprobe import tracktypes



def parseargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=mediaprobe.__doc__)
    parser.add_argument('-i', action="append", help="Input file path", required=True, metavar="<filepath>")
    parser.add_argument('-all', action='store_true', help="Returns the framerate")
    parser.add_argument('-fps', action='store_true', help="Returns the framerate")
    parser.add_argument('-duration', action='store', help="Returns the duration in frames or tc (if available)",
                        choices=["frames", "tc"], metavar="<frames|tc>")
    parser.add_argument('-search', action="store", help="Search for a specific field in mediainfo (case sensitive). " +
                        f"Also requires a track type {tuple([x.value for x in tracktypes])}", nargs=2, metavar=("<field>", "<tracktype>"))

    args = parser.parse_args()
    # args = parser.parse_args(f"-h".split())
    # args = parser.parse_args(f"-i {mediaprobe.testfile} -all".split())
    # args = parser.parse_args(f"-i {mediaprobe.testfile} -fps".split())
    # args = parser.parse_args(f"-i {mediaprobe.testfile} -duration tc".split())
    # args = parser.parse_args(f"-i {mediaprobe.testfile} -search Format_Profile video".split())
    

    if len([x for x in args.__dict__.values() if x != False and x != None]) > 2:
        print("Too many arguments. Only use one at a time. However, you may specify more then one input. Examples:\n"
                "-i /path/to/file.mov -i /path/to/anotherfile.mov -fps\n"
                "-i /path/to/file.mov -i /path/to/anotherfile.mov -search Format_Profile video\n")
        exit(2)

    if args.duration:
        args.duration = True if args.duration == "frames" else False

    if args.search:
        try:
            args.search[1] = mediaprobe.get_tracktype(args.search[1].lower().capitalize())
        except ValueError:
            print(f"'{args.search[1]}' is not a valid track type")
            exit(2)

    for file in args.i:
        if not Path(file).is_file():
            print(f"File not found: {file}")
            exit(2)

    return args

def prettyprintall(results: dict) -> None:
    for track in results['tracks']:
        for k,v in track.items():
            if k == "@type":
                print("\n")
            print(f"{k} = {v}")

def run() -> None:
    args = parseargs()
    for file in args.i:
        if args.all:
            results = mediaprobe.all(file)
            if results:
                print('\n')
                print(results.pop('path'))
                prettyprintall(results)
        if args.fps:
            print(mediaprobe.fps(file))
        if args.duration != None:
            print(mediaprobe.duration(file, args.duration))
        if args.search:
            print(mediaprobe.search(file, args.search[0], args.search[1]))


if __name__ == "__main__":
    run()