import argparse
import os
import subprocess

from socialresearchcv.analysis.Preprocessor import preprocess_files


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


if __name__ == '__main__':
    # Create the parser
    parser = argparse.ArgumentParser()
    # Add an argument
    parser.add_argument('--sampled', type=dir_path, required=True, help="path to sampled videos CSV folder")
    parser.add_argument('--scripted', type=dir_path, required=True, help="path to scripted videos CSV folder")
    # Parse the argument
    args = parser.parse_args()
    sampled = [[os.path.join(args.sampled, sample)] for sample in os.listdir(args.sampled)]
    scripted = [[os.path.join(args.scripted, script)] for script in os.listdir(args.scripted)]
    titles = sampled + scripted

    print(titles)
    # process the files
    print("1. Preprocessing the CSV files")
    preprocess_files(titles)

    # run preprocessing R script
    cmd1 = ['Rscript', '--vanilla', f'{os.getcwd()}/rcode/3DSR_data_prep.R', os.getcwd()]
    print(f"2. Preprocessing the R files using command: {cmd1}")
    print(cmd1)
    subprocess.run(cmd1)

    # run analysis R script
    cmd2 = ['Rscript', '--vanilla', f'{os.getcwd()}/rcode/3DSR_analysis.R', os.getcwd()]
    print(f"3. Performing 3DSR analysis using command: {cmd2}")
    subprocess.run(cmd2)

    print("ALL DONE!")
