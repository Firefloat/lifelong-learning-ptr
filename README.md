# Install Blender

Go to [this](https://download.blender.org/release/Blender2.79/) webpage and download blender-2.79b-windows64.zip for windows.

> **NOTE**: It is important that you download the version 2.79**b** and not 2.79 or 2.79a.

Unzip the `.zip` in any location you want. Check if blender works by simply double-clicking the `blender.exe` within the unzipped folder.

# Install Pybullet

> **NOTE**: Installing Pybullet is only necessary if you want to use the physics part of the PTR image generation. If you don't want to use that you can continue with [Installing pip](#install-pip)

1. Download the [Windows x86-64 executable installer](https://www.python.org/downloads/release/python-353/). This needs to be done because the standard blender python version does not come with the necessary header files attached.

2. Rename your python folder within the blender installation path, e.g. within `..\blender-2.79b-windows64\blender-2.79b-windows64\2.79` should be located a folder named `python`. Simply rename it to `python_bak`

3. Execute the Python executable that you downloaded in step `1`. 

   1. Uncheck `add to path`
   2. Check only `install precompiled standard libaries` and `install pip`
   3. **IMPORTANT:** do not choose the default location, but rather modify the installation path to be within your `blender/2.79/` folder, e.g. `..\blender-2.79b-windows64\blender-2.79b-windows64\2.79\python` (you need to create the `python` folder by yourself). This enables us to use that python version within blender.

4. Move to the installation `python` folder, there you should find a `python.exe`. Run the following command:

```shell
python.exe -m pip install pybullet
```

5. If you get no error -> good. If you get an error follow step 6.
6. If your error has something to do with C++ versions, please install the correct version through Visual Studio Installer
7. If you get an error `rc.exe` not found you need to go to the folder `C:\Program Files (x86)\Windows Kits` and search in all folders for the `rc.exe`
8. Add the folder with the `rc.exe` to your path and restart the console
9. You should be good to go and can install also numpy and pillow with the above command.


# Install pip

>**NOTE:** If you have already done the steps in [Install Pybullet](#install-pybullet) pip should already be installed in the bleder python version and you can continue with [Install dependencies](#install-dependencies).

Blender 2.79x does come with a Python 3.5 interpreter which will invoke the scripts that are used in this project. One of the pitfalls is that the interpreter does not come with `pip` which makes installing third party libraries impossible.

To install `pip` navigate to the unzipped folder under `..blender-2.79b-windows64\2.79\python\bin` in your terminal. After that execute the `python.exe` that you find in that directory and pass the `get-pip.py` script, that you can find in this project root directory by typing:

```shell
./python.exe /path/to/get-pip.py
```

> **NOTE**: if you use powershell or cmd you need to adjust the path to windows paths, i.e. path\to\get-pip.py.
> Furthermore it is possible that you need to omit the `./` infront of `python.exe`

## Install dependencies

After successfull installation of `pip` you can install `pillow` which is required by [render_images_partnet.py](data_generation/image_generation/render_images_partnet.py) by typing

> **NOTE**: you need to be located in the same directory as in the previous example where we installed pip!

```shell
./python.exe -m pip install pillow
```

## Add blender to path

To make the `blender` command available in your system you need to add the unzipped folder path (up until you can see the `blender.exe`) to your system path (environment variable). 

# Download Datasets

To make the project run you need to download [Partnet Dataset](https://shapenet.org/login/) (you need an account) and [Partnet Mobility Dataset](https://sapien.ucsd.edu/browse) (you need an account too). 

> **NOTE**: The first data set is quite large, i.e. the zip to download is around `100 GB` and the unzipped data set is around `322 GB`. The second data set is *only* `~10 GB`.

Unzip both dataset in any location that is convenient.

# Run render_images_partnet.py

To run [render_images_partnet.py](data_generation/image_generation/render_images_partnet.py) you need to navigate to the location of the script first.

> **NOTE**: I have adjusted some paths and it should work from anywhere, but to be completely sure navigation to the `image_generation` folder is advised.

To generate images use the following command:

```shell
blender --python render_images_partnet.py --background -- --data_dir /path/to/unzipped/partnet --mobility_dir /path/to/unzipped/partnet/mobility --use_gpu 1
```

The last flag `--use_gpu 1` enables blender to run on your gpu. This only works if you have a NVIDIA Gpu and CUDA installed. Otherwise you can use `--use_gpu 0` or omit the flag.


python generate_questions_partnet.py --input_scene_files ../output/scenes/ --output_dir out/ --output_questions_file out/PARTNET_questions.json
