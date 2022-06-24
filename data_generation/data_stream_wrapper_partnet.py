import argparse
from datetime import datetime as dt
import pathlib
import random
from signal import signal, SIGINT
import subprocess
import sys


IMAGE_DIR = pathlib.Path(__file__).parent / 'image_generation'
IMAGE_DATA_DIR = IMAGE_DIR / 'data'
IMAGE_OUTPUT_DIR = IMAGE_DIR.parent / 'output'
ROOT_DIR = pathlib.Path(__file__).parent
TEMPLATE_ORDER = [
    'single_object',
    'what_question',
    'same_relate',
    'analogy',
    'arithmetic',
    'physics',
    'comparison',
    'geometry',
    'one_hop',
    'zero_hop',
]
_NO_DIR = object()


class FolderStructure:
    """Class that encapsulates the folder structure for a single run"""

    def __init__(self, root: pathlib.Path) -> None:
        self._root = root.absolute()

    @property
    def root(self) -> pathlib.Path:
        return self._root

    @property
    def image_dir(self) -> pathlib.Path:
        return self.root / 'images'

    @property
    def scene_dir(self) -> pathlib.Path:
        return self.root / 'scenes'

    @property
    def depth_dir(self) -> pathlib.Path:
        return self.root / 'depths'

    @property
    def scene_file(self) -> pathlib.Path:
        return self.root / 'ptr_scenes.json'

    @property
    def blend_dir(self) -> pathlib.Path:
        return self.root / 'blendfiles'

    @property
    def question_file(self) -> pathlib.Path:
        return self.root / 'questions.json'


def get_folder_number(dir: pathlib.Path) -> int:
    """Gets an incremental number for a folder, depending on how the other
    folders are numbered, e.g. if a folder A contains the folders run_1 and 
    run_2 the call to this function with get_folder_number(A) will return 3.

    Parameters
    ----------
    dir : pathlib.Path
        Directory containing numbered folders

    Returns
    -------
    int
        Next number for folder
    """
    nums = [
        int(str(d.name).split('_')[1]) for d in dir.iterdir()
        if str(d.name).split('_')[1].isnumeric()
    ]
    nums = sorted(nums)

    if not nums:
        return 0

    return nums[-1] + 1


def is_windows() -> bool:
    return 'win' in sys.platform


def assert_root_folder(arg_path) -> pathlib.Path:
    """Makes sure the root folder for the output exists

    Parameters
    ----------
    arg_path : Any
        Path that was passed by the user

    Returns
    -------
    pathlib.Path
        Path to the root folder for the output
    """
    if arg_path is _NO_DIR:
        arg_path = ROOT_DIR / 'out'
        arg_path.mkdir(exist_ok=True)
        directory_number = get_folder_number(arg_path)
        arg_path = arg_path / f'run_{directory_number}'

    arg_path.mkdir(parents=True, exist_ok=True)
    return arg_path


class FolderCreator:
    """Class that creates the project folder structure"""

    def __init__(self, root_dir) -> None:

        root_dir = pathlib.Path(root_dir)

        if not root_dir.exists():
            pass
        elif root_dir.is_file():
            raise RuntimeError(
                f"Output directory {root_dir} is a file!"
            )
        elif any(root_dir.iterdir()):
            raise RuntimeError(
                f"Output directory {root_dir} is not empty!"
            )

        self._folder_structure = FolderStructure(root_dir)
        self._folder_structure.root.mkdir(parents=True, exist_ok=True)

    @property
    def structure(self) -> FolderStructure:
        return self._folder_structure

    def create_file_structure(self) -> None:
        self.structure.image_dir.mkdir()
        self.structure.scene_dir.mkdir()
        self.structure.depth_dir.mkdir()
        self.structure.blend_dir.mkdir()


def run_subprocess(command: str):
    """Runs a command in a subprocess and prints the output to the current
    console.

    Parameters
    ----------
    command : str
        Command to execute
    """
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )

    def kill_proc(signal_received, frame):
        print("CTRL-C detected, exiting gracefully")
        process.kill()
        exit(0)

    signal(SIGINT, kill_proc)

    try:
        for ln in iter(lambda: process.stdout.readline(), b""):  # type: ignore
            sys.stdout.write(ln.decode('utf-8'))
    except Exception:
        process.kill()


def get_bash_prefix(bash_path) -> str:
    """Generates the correct bash-prefix for Windows systems, because the
    code currently works only with the git-bash.

    Parameters
    ----------
    bash_path : str/pathlib.Path
        User arguments

    Returns
    -------
    str
        Correct prefix

    Raises
    ------
    FileNotFoundError
        If the git-bash path cannot be found an exception is raised
    """
    bash_prefix = ''

    if is_windows():
        git_bash_path = pathlib.Path(bash_path)
        if not git_bash_path.exists():
            raise FileNotFoundError(
                f"Git bash could not be found in path {git_bash_path}. Please "
                "use the option --bash_path and specify where the git-bash "
                "can be found on your system."
            )

        bash_prefix = f'"{str(git_bash_path)}" -i -c "'

    return bash_prefix


def generate_images(
    *,
    args,
    bash_prefix: str,
    folder_structure: FolderStructure,
    min_objects: int,
    max_objects: int,
    num_images: int,

) -> None:

    run_subprocess(
        f'{bash_prefix}blender --python \
        image_generation/render_images_partnet.py --background -- \
        --min_objects {min_objects} \
        --max_objects {max_objects} \
        --min_dist {args.min_objects} \
        --margin {args.margin} \
        --margin2 {args.margin2} \
        --min_pixels_per_object {args.min_pixels_per_object} \
        --max_retries {args.max_retries} \
        --start_idx {args.start_idx} \
        --num_images {num_images} \
        --filename_prefix {args.filename_prefix} \
        --split {args.split} \
        --output_image_dir {folder_structure.image_dir.as_posix()} \
        --output_scene_dir {folder_structure.scene_dir.as_posix()} \
        --output_depth_dir {folder_structure.depth_dir.as_posix()} \
        --output_scene_file {folder_structure.scene_file.as_posix()}\
        --output_blend_dir {folder_structure.blend_dir.as_posix()} \
        --save_blendfiles {args.save_blendfiles} \
        --version {args.version} \
        --date {args.date} \
        --use_gpu {args.use_gpu} \
        --width {args.width} \
        --height {args.height} \
        --key_light_jitter {args.key_light_jitter} \
        --fill_light_jitter {args.fill_light_jitter} \
        --back_light_jitter {args.back_light_jitter} \
        --camera_jitter {args.camera_jitter} \
        --render_num_samples {args.render_num_samples} \
        --render_min_bounces {args.render_min_bounces} \
        --render_max_bounces {args.render_max_bounces} \
        --render_tile_size {args.render_tile_size} \
        --data_dir {args.data_dir} \
        --mobility_dir {args.mobility_dir}'
    )


def generate_questions(
    *,
    args,
    folder_structure: FolderStructure,
    instances_per_template: int,
    template_types: str,
) -> None:
    run_subprocess(
        f'python question_generation/generate_questions_partnet.py \
        --input_scene_files {folder_structure.scene_dir.as_posix()} \
        --metadata_file {args.metadata_file} \
        --synonyms_json {args.synonyms_json} \
        --template_dir {args.template_dir} \
        --output_dir {folder_structure.root.as_posix()} \
        --output_questions_file {folder_structure.question_file.as_posix()} \
        --scene_start_idx {args.scene_start_idx} \
        --num_scenes {args.num_scenes} \
        --templates_per_image {args.templates_per_image} \
        --instances_per_template {instances_per_template} \
        --template_types {template_types} \
        --reset_counts_every {args.reset_counts_every}',
    )


def main_loop(args) -> None:
    args = parse_args()
    bash_prefix = get_bash_prefix(args.bash_path)
    root_folder = assert_root_folder(args.out)

    for index, template_type in enumerate(TEMPLATE_ORDER):
        print(f"Creating images and questions for '{template_type}'")

        creator = FolderCreator(root_folder / f"{index + 1}_{template_type}")
        creator.create_file_structure()

        print(f"\nOutputfolder for current run: {creator.structure.root}\n")

        print("Generating output images, this can take a while...")
        generate_images(
            args=args,
            bash_prefix=bash_prefix,
            folder_structure=creator.structure,
            min_objects=args.min_objects,
            max_objects=args.max_objects,
            num_images=args.num_images,
        )

        print("Generating questions")
        generate_questions(
            args=args,
            folder_structure=creator.structure,
            instances_per_template=args.instances_per_template,
            template_types=template_type,
        )


def main():
    args = parse_args()
    main_loop(args)


def parse_args():
    parser = argparse.ArgumentParser()

    # Input options
    parser.add_argument(
        '--out',
        default=_NO_DIR,
        help='Directory for all the outputs'
    )
    parser.add_argument(
        '--bash_path',
        default=pathlib.Path("C:/Program Files/Git/bin/sh.exe"),
        help='Only for Windows systems, path to the git-bash'
    )
    # Settings for objects
    parser.add_argument(
        '--min_objects',
        default=3,
        type=int,
        help="The minimum number of objects to place in each scene"
    )
    parser.add_argument(
        '--max_objects',
        default=6,
        type=int,
        help="The maximum number of objects to place in each scene"
    )
    parser.add_argument(
        '--margin',
        default=1.5,
        type=float,
        help="Along all cardinal directions (left, right, front, back), all " +
             "objects will be at least this distance apart. This makes resolving " +
             "spatial relationships slightly less ambiguous."
    )
    parser.add_argument(
        '--margin2',
        default=8,
        type=float,
        help="Along all cardinal directions (left, right, front, back), all " +
             "objects will be at least this distance apart. This makes resolving " +
             "spatial relationships slightly less ambiguous."
    )
    parser.add_argument(
        '--min_pixels_per_object',
        default=200,
        type=int,
        help="All objects will have at least this many visible pixels in the " +
             "final rendered images; this ensures that no objects are fully " +
             "occluded by other objects."
    )
    parser.add_argument(
        '--max_retries',
        default=20000,
        type=int,
        help="The number of times to try placing an object before giving up and " +
             "re-placing all objects in the scene."
    )

    # Output settings
    parser.add_argument(
        '--start_idx',
        default=0,
        type=int,
        help="The index at which to start for numbering rendered images. Setting " +
             "this to non-zero values allows you to distribute rendering across " +
             "multiple machines and recombine the results later."
    )
    parser.add_argument(
        '--num_images',
        default=5,
        type=int,
        help="The number of images to render"
    )
    parser.add_argument(
        '--filename_prefix',
        default='PTR',
        help="This prefix will be prepended to the rendered images and JSON scenes"
    )
    parser.add_argument(
        '--split',
        default='new',
        help="Name of the split for which we are rendering. This will be added to " +
             "the names of rendered images, and will also be stored in the JSON " +
             "scene structure for each image."
    )
    parser.add_argument(
        '--save_blendfiles',
        type=int,
        default=0,
        help="Setting --save_blendfiles 1 will cause the blender scene file for " +
             "each generated image to be stored in the directory specified by " +
             "the --output_blend_dir flag. These files are not saved by default " +
             "because they take up ~5-10MB each."
    )
    parser.add_argument(
        '--version',
        default='1.0',
        help="String to store in the \"version\" field of the generated JSON file"
    )
    parser.add_argument(
        '--license',
        default="Creative Commons Attribution (CC-BY 4.0)",
        help="String to store in the \"license\" field of the generated JSON file"
    )
    parser.add_argument(
        '--date',
        default=dt.today().strftime("%m/%d/%Y"),
        help="String to store in the \"date\" field of the generated JSON file; " +
             "defaults to today's date"
    )

    # Rendering options
    parser.add_argument(
        '--use_gpu',
        default=1,
        type=int,
        help="Setting --use_gpu 1 enables GPU-accelerated rendering using CUDA. " +
             "You must have an NVIDIA GPU with the CUDA toolkit installed for " +
             "to work."
    )
    parser.add_argument(
        '--width',
        default=800,
        type=int,
        help="The width (in pixels) for the rendered images"
    )
    parser.add_argument(
        '--height',
        default=600,
        type=int,
        help="The height (in pixels) for the rendered images"
    )
    parser.add_argument(
        '--key_light_jitter',
        default=1.0,
        type=float,
        help="The magnitude of random jitter to add to the key light position."
    )
    parser.add_argument(
        '--fill_light_jitter',
        default=1.0,
        type=float,
        help="The magnitude of random jitter to add to the fill light position."
    )
    parser.add_argument(
        '--back_light_jitter',
        default=1.0,
        type=float,
        help="The magnitude of random jitter to add to the back light position."
    )
    parser.add_argument(
        '--camera_jitter',
        default=0.5,
        type=float,
        help="The magnitude of random jitter to add to the camera position"
    )
    parser.add_argument(
        '--render_num_samples',
        default=512,
        type=int,
        help="The number of samples to use when rendering. Larger values will " +
            "result in nicer images but will cause rendering to take longer."
    )
    parser.add_argument(
        '--render_min_bounces',
        default=8,
        type=int,
        help="The minimum number of bounces to use for rendering."
    )
    parser.add_argument(
        '--render_max_bounces',
        default=8,
        type=int,
        help="The maximum number of bounces to use for rendering."
    )
    parser.add_argument(
        '--render_tile_size',
        default=256,
        type=int,
        help="The tile size to use for rendering. This should not affect the " +
             "quality of the rendered image but may affect the speed; CPU-based " +
             "rendering may achieve better performance using smaller tile sizes " +
             "while larger tile sizes may be optimal for GPU-based rendering."
    )

    parser.add_argument('--data_dir', default=str(IMAGE_DIR / 'data_v0'), type=str)
    parser.add_argument('--mobility_dir', default=str(IMAGE_DIR / 'cart'), type=str)

    # question generation arguments
    parser.add_argument('--metadata_file', default='question_generation/metadata_partnet.json',
                        help="JSON file containing metadata about functions")
    parser.add_argument('--synonyms_json', default='question_generation/synonyms.json',
                        help="JSON file defining synonyms for parameter values")
    parser.add_argument('--template_dir', default='question_generation/PARTNET_templates',
                        help="Directory containing JSON templates for questions")
    # Control which and how many images to process
    parser.add_argument('--scene_start_idx', default=0, type=int,
                        help="The image at which to start generating questions; this allows " +
                            "question generation to be split across many workers")
    parser.add_argument('--num_scenes', default=0, type=int,
                        help="The number of images for which to generate questions. Setting to 0 " +
                            "generates questions for all scenes in the input file starting from " +
                            "--scene_start_idx")

    # Control the number of questions per image; we will attempt to generate
    # templates_per_image * instances_per_template questions per image.
    parser.add_argument('--templates_per_image', default=10, type=int,
                        help="The number of different templates that should be instantiated " +
                            "on each image")
    parser.add_argument('--instances_per_template', default=1, type=int,
                        help="The number of times each template should be instantiated on an image")

    # Misc
    parser.add_argument('--reset_counts_every', default=6000, type=int,
                        help="How often to reset template and answer counts. Higher values will " +
                            "result in flatter distributions over templates and answers, but " +
                            "will result in longer runtimes.")
    return parser.parse_args()


if __name__ == '__main__':
    main()
