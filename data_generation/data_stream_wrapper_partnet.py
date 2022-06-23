import argparse
from datetime import datetime as dt
import pathlib
from signal import signal, SIGINT
import subprocess
import sys


IMAGE_DIR = pathlib.Path(__file__).parent / 'image_generation'
IMAGE_DATA_DIR = IMAGE_DIR / 'data'
IMAGE_OUTPUT_DIR = IMAGE_DIR.parent / 'output'
ROOT_DIR = pathlib.Path(__file__).parent
_NO_DIR = object()


class FolderStructure:

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
    nums = [
        int(str(d).split('_')[1]) for d in dir.iterdir()
        if str(d).split('_')[1].isnumeric()
    ]
    nums = sorted(nums)

    if not nums:
        return 0

    return nums[-1] + 1


def assert_root_folder(arg_path) -> pathlib.Path:
    if arg_path is _NO_DIR:
        arg_path = ROOT_DIR / 'out'
        arg_path.mkdir(exist_ok=True)
        directory_number = get_folder_number(arg_path)
        arg_path = arg_path / f'run_{directory_number}'

    arg_path.mkdir(parents=True, exist_ok=True)
    return arg_path


class FolderCreator:

    def __init__(self, root_dir) -> None:

        root_dir = pathlib.Path(root_dir)

        if root_dir.is_file():
            raise RuntimeError(
                f"Output directory {self.structure.root} is a file!"
            )
        elif any(root_dir.iterdir()):
            raise RuntimeError(
                f"Output directory {self.structure.root} is not empty!"
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


def run_subprocess(command):

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
        for line in iter(lambda: process.stdout.readline(), b""):
            sys.stdout.write(line.decode('utf-8'))
    except Exception:
        process.kill()


def generate_images(
    *,
    args,
    folder_structure: FolderStructure,
    min_objects: int,
    max_objects: int,
    num_images: int,

) -> None:

    # replace git-bash for "{path_to_git_directory}/Git/bin/sh" in the
    # following command to see more detailed errors
    run_subprocess(
        f'"C:\\Program Files\\Git\\bin\\sh" -i -c "blender --python \
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


def main_loop(args):
    args = parse_args()
    root_folder = assert_root_folder(args.out)

    creator = FolderCreator(root_folder)
    creator.create_file_structure()

    print(f"\nOutputfolder: {creator.structure.root}\n")

    image_output = generate_images(
        args=args,
        folder_structure=creator.structure,
        min_objects=args.min_objects,
        max_objects=args.max_objects,
        num_images=args.num_images,
    )
    question_output = generate_questions(
        args=args,
        folder_structure=creator.structure,
        instances_per_template=args.instances_per_template,
        template_types=args.template_types,
    )

    return image_output, question_output


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
        '--base_scene_blendfile',
        default=str(IMAGE_DIR / 'base_scene.blend'),
        help="Base blender file on which all scenes are based; includes " +
             "ground plane, lights, and camera."
    )
    parser.add_argument(
        '--properties_json',
        default=str(IMAGE_DATA_DIR / 'properties_partnet.json')
    )
    parser.add_argument('--tmp_dir', default=str(IMAGE_DIR / 'tmp9'))
    parser.add_argument(
        '--material_dir',
        default=str(IMAGE_DIR / 'materials'),
        help="Directory where .blend files for materials are stored"
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
        '--min_dist',
        default=0.25,
        type=float,
        help="The minimum allowed distance between object centers"
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

    # Control what kind type of templates to use
    parser.add_argument('--template_types', default='*',
                        help='The types of templates to be used as a comma-separated list. * means use all')

    # Misc
    parser.add_argument('--reset_counts_every', default=6000, type=int,
                        help="How often to reset template and answer counts. Higher values will " +
                            "result in flatter distributions over templates and answers, but " +
                            "will result in longer runtimes.")
    parser.add_argument('--verbose', action='store_true',
                        help="Print more verbose output")
    parser.add_argument('--time_dfs', action='store_true',
                        help="Time each depth-first search; must be given with --verbose")
    parser.add_argument('--profile', action='store_true',
                        help="If given then run inside cProfile")
    return parser.parse_args()


if __name__ == '__main__':
    main()
