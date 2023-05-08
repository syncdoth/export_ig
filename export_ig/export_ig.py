import glob
import os
from dataclasses import dataclass, field

from joblib import Parallel, delayed
from PIL import Image
from simple_parsing import ArgumentParser

from .shadow_pad import ShadowPadOptions, shadow_pad


@dataclass
class Options:
    input_path: str = field(metadata={"help": "Path to the image or folder of images to process"})
    output_folder: str = field(metadata={"help": "Path to the output folder"})
    subfolder: bool = field(default=True,
                            metadata={"help": "Whether to create a subfolder in the output folder"})
    n_jobs: int = field(default=-1, metadata={"help": "Number of jobs to run in parallel"})


def main():
    parser = ArgumentParser()
    parser.add_arguments(ShadowPadOptions, dest="shadow_pad")
    parser.add_arguments(Options, dest="options")
    args = parser.parse_args()

    input_path = args.options.input_path
    if os.path.isdir(input_path):
        input_path = os.path.join(input_path, "*")

    files = [f for f in glob.glob(input_path) if not os.path.isdir(f)]
    if len(files) == 0:
        raise ValueError("No files found")

    output_folder = args.options.output_folder
    if args.options.subfolder:
        output_folder = os.path.join(os.path.dirname(input_path), output_folder)
    os.makedirs(output_folder, exist_ok=True)

    process = shadow_pad(args.shadow_pad)

    def _process_image(input_file_path):
        image = Image.open(input_file_path)
        padded = process(image)
        basename = os.path.basename(input_file_path)
        fname, ext = os.path.splitext(basename)
        out_fname = os.path.join(output_folder, fname + "-padded" + ext)
        padded.save(out_fname)

    Parallel(n_jobs=args.options.n_jobs)(delayed(_process_image)(fname) for fname in files)


if __name__ == '__main__':
    main()
