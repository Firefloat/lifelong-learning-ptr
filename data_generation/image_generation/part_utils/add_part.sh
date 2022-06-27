blendFile=$1
objpath=$2
pngpath=$3
blender --background -noaudio --python image_generation/part_utils/add_part.py -- $blendFile $objpath $pngpath > /dev/null
