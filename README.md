# PTR: A Benchmark for Part-based Conceptual, Relational, and Physical Reasoning

![Dataset Overview](http://ptr.csail.mit.edu/assets/teaser.png)

**Figure 1. Dataset Overview.**

## Introduction

A critical aspect of human visual perception is the ability to parse visual scenes into individual objects and further into object parts, forming part-whole hierarchies. Such composite structures could induce a rich set of semantic concepts and relations, thus playing an important role in the interpretation and organization of visual signals as well as for the generalization of visual perception and reasoning. However, existing visual reasoning benchmarks mostly focus on objects rather than parts. Visual reasoning based on the full part-whole hierarchy is much more challenging than object-centric reasoning due to finer-grained concepts, richer geometry relations, and more complex physics. Therefore, to better serve for part-based conceptual, relational and physical reasoning, we introduce a new large-scale diagnostic visual reasoning dataset named PTR. PTR contains around 70k RGBD synthetic images with ground truth object and part level annotations regarding semantic instance segmentation, color attributes, spatial and geometric relationships, and certain physical properties such as stability. These images are paired with 700k machine-generated questions covering various types of reasoning types, making them a good testbed for visual reasoning models. We examine several state-of-the-art visual reasoning models on this dataset and observe that they still make many surprising mistakes in situations where humans can easily infer the correct answer. We believe this dataset will open up new opportunities for part-based reasoning.

PTR is accepted by NeurIPS 2021.

Authors: [Yining Hong](https://evelinehong.github.io/), [Li Yi](https://cs.stanford.edu/~ericyi/), [Joshua B Tenenbaum](http://web.mit.edu/cocosci/josh.html), [Antonio Torralba](http://web.mit.edu/cocosci/josh.html) and [Chuang Gan](https://people.csail.mit.edu/ganchuang/) from UCLA, MIT, IBM, Stanford and Tsinghua.

Arxiv Version: https://arxiv.org/abs/2112.05136

Project Page: http://ptr.csail.mit.edu/

## Download
Data and evaluation server can be found [here](http://ptr.csail.mit.edu/)

## TODOs
Data generation codes and baseline models will be available soon!
(Currently we provide a rough version of the data generation codes, which will be arranged later)

## Errata
We have manually examined the images, annotations and questions twice. However, provided that there are annotation errors of the PartNet dataset we used, there could still be some errors in the scene annotations. **If you find any errors that make the questions unanswerable, please contact yninghong@gmail.com**. 

## About the Data
The data includes train/val/test images / questions / scene annotations / depths. 
Note that due to data cleaning process, the indices of the images are not necessarily consecutive.

The scene annotation is a json file that contains the following keys:
```
    cam_location        #location of the camera
    cam_rotation        #rotation of the camera
    directions          #Based on the camera, the vectors of the directions
    image_filename      #the filename of the image
    image_index         #the index of the image
    objects             #the objects in the scene, which contains a list of objects
        3d_coords       #the location of the object
        category        #the object category
        line_geo        #a dictionary containing (part, line unit normal vector) pairs. See the [unit normal vector](https://sites.math.washington.edu/~king/coursedir/m445w04/notes/vector/normals-plane.html) of a line. If the vector is not a unit vector, then the part cannot be considered a line.
        plane_geo       #a dictionary containing (part, plane unit normal vector) pairs. See the [unit normal vector](https://sites.math.washington.edu/~king/coursedir/m445w04/notes/vector/normals-plane.html) of a plane. If the vector is not a unit vector, then the part cannot be considered a line.
        obj_mask        #the mask of the object
        part_color      #a dictionary containing the colors of the parts
        part_count      #a dictionary containing the number of the parts
        part_mask       #a dictionary containing the masks of the parts
        partnet_id      #the id of the original partnet object in the PartNet dataset
        pixel_coords    #the pixel of the object
    relationships       #according to the directions, the spatial relationships of the objects
    projection_matrix   #the projection matrix of the camera to reconstruct 3D scene using depths
```

## Citations
    @inproceedings{hong2021ptr,
    author = {Hong, Yining and Yi, Li and Tenenbaum, Joshua B and Torralba, Antonio and Gan, Chuang},
    title = {PTR: A Benchmark for Part-based Conceptual, Relational, and Physical Reasoning},
    booktitle = {Advances In Neural Information Processing Systems},
    year = {2021}
    }