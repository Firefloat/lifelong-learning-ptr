import argparse
import pathlib
import subprocess
from datetime import datetime as dt

parser = argparse.ArgumentParser()

IMAGE_DIR = pathlib.Path(__file__).parent / 'image_generation'
IMAGE_DATA_DIR = IMAGE_DIR / 'data'
IMAGE_OUTPUT_DIR = IMAGE_DIR.parent / 'output'
ROOT_DIR = str(pathlib.Path(__file__).parent).replace('\\', '/')

# image generation arguments

# Input options
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
    '--output_image_dir',
    default=str(IMAGE_OUTPUT_DIR / 'images'),
    help="The directory where output images will be stored. It will be " +
         "created if it does not exist."
)
parser.add_argument(
    '--output_scene_dir',
    default=str(IMAGE_OUTPUT_DIR / 'scenes'),
    help="The directory where output JSON scene structures will be stored. " +
         "It will be created if it does not exist."
)
parser.add_argument(
    '--output_depth_dir',
    default=str(IMAGE_OUTPUT_DIR / 'depths'),
    help="The directory where output JSON scene structures will be stored. " +
         "It will be created if it does not exist."
)
parser.add_argument(
    '--output_scene_file',
    default=str(IMAGE_OUTPUT_DIR / 'ptr_scenes.json'),
    help="Path to write a single JSON file containing all scene information"
)
parser.add_argument(
    '--output_blend_dir',
    default=str(IMAGE_OUTPUT_DIR / 'blendfiles'),
    help="The directory where blender scene files will be stored, if the " +
         "user requested that these files be saved using the " +
         "--save_blendfiles flag; in this case it will be created if it does " +
         "not already exist."
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

# Inputs
parser.add_argument('--input_scene_files',
                    default='/home/evelyn/Desktop/partnet-reasoning/real_final_datasets/train/scenes_new',
                    help="JSON file containing ground-truth scene information for all images " +
                         "from render_images.py")
parser.add_argument('--metadata_file', default='question_generation/metadata_partnet.json',
                    help="JSON file containing metadata about functions")
parser.add_argument('--synonyms_json', default='question_generation/synonyms.json',
                    help="JSON file defining synonyms for parameter values")
parser.add_argument('--template_dir', default='question_generation/PARTNET_templates',
                    help="Directory containing JSON templates for questions")
parser.add_argument('--output_dir',
                    default='/home/evelyn/Desktop/partnet-reasoning/real_final_datasets/train/questions',
                    help="Directory containing JSON templates for questions")
# parser.add_argument('--new_scene_dir', default='../try_nscl/train/scenes_renew',
#     help="Directory containing JSON templates for questions")

# Output
parser.add_argument('--output_questions_file',
                    default='/home/evelyn/Desktop/partnet-reasoning/real_final_datasets/train/PARTNET_questions.json',
                    help="The output file to write containing generated questions")

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

args = parser.parse_args()


def generate_images():
    # "C:/Program Files/Git/bin/sh"
    output = subprocess.run(f'git-bash -i -c "blender --python image_generation/render_images_partnet.py --background -- \
    --base_scene_blendfile {args.base_scene_blendfile} \
    --properties_json {args.properties_json} \
    --material_dir {args.material_dir} \
    --min_objects {args.min_objects} \
    --max_objects {args.max_objects} \
    --min_dist {args.min_objects} \
    --margin {args.margin} \
    --margin2 {args.margin2} \
    --min_pixels_per_object {args.min_pixels_per_object} \
    --max_retries {args.max_retries} \
    --start_idx {args.start_idx} \
    --num_images {args.num_images} \
    --filename_prefix {args.filename_prefix} \
    --split {args.split} \
    --output_image_dir {args.output_image_dir} \
    --output_scene_dir {args.output_scene_dir} \
    --output_depth_dir {args.output_depth_dir} \
    --output_scene_file {args.output_scene_file} \
    --output_blend_dir {args.output_blend_dir} \
    --save_blendfiles {args.save_blendfiles} \
    --version {args.version} \
    --license {args.license} \
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
    --render_tile_size {args.render_title_size} \
    --data_dir {args.data_dir} \
    --mobility_dir {args.mobility_dir}',
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    print(output)


# --data_dir B:/PartNetData/partnet \
# --mobility_dir B:/PartNetData/mobility --use_gpu 1 \
# --output_image_dir {ROOT_DIR}/single_item/output/images \
# --output_scene_dir {ROOT_DIR}/single_item/output/scenes \
# --output_depth_dir {ROOT_DIR}/single_item/output/depths \
# --output_scene_file {ROOT_DIR}/single_item/output/ptr_scenes.json \
# --output_blend_dir {ROOT_DIR}/single_item/output/blendfiles \
# --num_images  1 \
# --min_objects 1 \
# --max_objects 1


def generate_questions():
    output = subprocess.run(f'python question_generation/generate_questions_partnet.py \
    --input_scene_files {args.input_scene_file} \
    --metadata_file {args.metadata_file} \
    --synonyms_json {args.synonyms_json} \
    --template_dir {args.template_dir} \
    --output_dir {args.output_dir} \
    --output_questions_file {args.output_questions_file} \
    --scene_start_idx {args.scene_start_idx} \
    --num_scenes {args.num_scenes} \
    --templates_per_image {args.templates_per_image} \
    --instances_per_template {args.instances_per_template} \
    --template_types {args.tmplate_types} \
    --reset_counts_every {args.reset_counts_every} \
    --verbose {args.verbose} \
    --time_dfs {args.time_dfs} \
    --profile {args.profile}',
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    # --instances_per_template 15 \
    # --template_types single_object \
    # --input_scene_files {ROOT_DIR}/single_item/output/scenes \
    # --output_dir {ROOT_DIR}/single_item/output \
    # --output_questions_file questions_file',
    print(output)


def main():
    generate_images()
    generate_questions()


if __name__ == '__main__':
    main()
