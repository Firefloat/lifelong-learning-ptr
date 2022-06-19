import argparse
import pathlib
import subprocess

parser = argparse.ArgumentParser()

ROOT_DIR = pathlib.Path(__file__).parent
print("THIS_DIR IS: ", ROOT_DIR)


def generate_images():
    #    output3 = subprocess.run(f'git-bash -i -c "blender --python image_generation/render_images_partnet.py --background -- --data_dir B:/PartNetData/partnet --mobility_dir B:/PartNetData/mobility --use_gpu 1 \
    output3 = subprocess.run('"C:/Program Files/Git/bin/sh" -i -c "blender --python image_generation/render_images_partnet.py --background -- --data_dir B:/PartNetData/partnet --mobility_dir B:/PartNetData/mobility --use_gpu 1 \
    --output_image_dir C:/Users/aonti/IdeaProjects/lifelong-learning-ptr-new2/data_generation/single_item/output/images \
    --output_scene_dir C:/Users/aonti/IdeaProjects/lifelong-learning-ptr-new2/data_generation/single_item/output/scenes \
    --output_depth_dir C:/Users/aonti/IdeaProjects/lifelong-learning-ptr-new2/data_generation/single_item/output/depths \
    --output_scene_file C:/Users/aonti/IdeaProjects/lifelong-learning-ptr-new2/data_generation/single_item/output/ptr_scenes.json \
    --output_blend_dir C:/Users/aonti/IdeaProjects/lifelong-learning-ptr-new2/data_generation/single_item/output/blendfiles \
    --num_images  1 \
    --min_objects 1 \
    --max_objects 1"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(output3)


def generate_questions():
    output4 = subprocess.run('python question_generation/generate_questions_partnet.py \
                              --instances_per_template 15  \
                              --template_types single_object  \
                              --input_scene_files C:/Users/aonti/IdeaProjects/lifelong-learning-ptr-new2/data_generation/single_item/output/scenes  \
                              --output_dir C:/Users/aonti/IdeaProjects/lifelong-learning-ptr-new2/data_generation/single_item/output/questions  \
                              --output_questions_file questions_file',
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    print(output4)


def main():
    generate_images()
    generate_questions()


if __name__ == '__main__':
    main()
