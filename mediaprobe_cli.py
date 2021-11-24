import argparse
from pathlib import Path

import mediaprobe
from mediaprobe import Tracktypes


def parseargs() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=mediaprobe.__doc__)
    parser.add_argument('-i', action="append", help="Input file path", required=True, metavar="<filepath>")
    parser.add_argument('-all', action='store_true', help="Returns the framerate")
    parser.add_argument('-fps', action='store_true', help="Returns the framerate")
    parser.add_argument('-frames', action='store_true', help="Returns the total number of frames")
    parser.add_argument('-search', action="store", help="Search for a specific field in mediainfo (case sensitive). " +
                        f"Requires a track type {tuple([x.value for x in Tracktypes])}", nargs=2, metavar=("<field>", "<tracktype>"))

    args = parser.parse_args()
    # ------ Debug
    # args = parser.parse_args(f"-h".split())
    # args = parser.parse_args(f"-i {mediaprobe.testfile} -all".split())
    # args = parser.parse_args(f"-i {mediaprobe.testfile} -fps".split())
    # args = parser.parse_args(f"-i {mediaprobe.testfile} -frames tc".split())
    # args = parser.parse_args(f"-i {mediaprobe.testfile} -search Format_Profile video".split())
    

    if len([x for x in args.__dict__.values() if x != False and x != None]) > 2:
        print("Too many arguments. Only use one at a time. However, you may specify more then one input. Examples:\n"
                "-i /path/to/file.mov -i /path/to/anotherfile.mov -fps\n"
                "-i /path/to/file.mov -i /path/to/anotherfile.mov -search Format_Profile video\n")
        exit(2)

    if args.search:
        try:
            args.search[1] = mediaprobe.get_tracktype_enum(args.search[1])
        except ValueError:
            print(f"'{args.search[1]}' is not a valid track type")
            exit(2)

    for file in args.i:
        if not Path(file).is_file():
            print(f"File not found: {file}")
            exit(2)

    return args

def prettyprintall(fulloutput: dict) -> None:
    '''
    Cleans up the full JSON output from mediainfo
    and prints it line by line
    '''
    for track in fulloutput['tracks']:
        for k,v in track.items():
            if k == "@type":
                print("\n")
            print(f"{k} = {v}")

def run() -> None:
    args = parseargs()
    for file in args.i:
        if args.all:
            fulloutput = mediaprobe.all(file)
            if fulloutput:
                print('\n')
                print(fulloutput.pop('path'))
                prettyprintall(fulloutput)
        if args.fps:
            print(mediaprobe.fps(file))
        if args.framecount:
            print(mediaprobe.framecount(file))
        if args.search:
            print(mediaprobe.search(file, args.search[0], args.search[1]))


if __name__ == "__main__":
    run()