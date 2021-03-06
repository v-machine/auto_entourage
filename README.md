# Auto Entourage
Auto Entourage is a small Grasshopper plugin for loading entourage images(.png format) from an image folder into Rhino.

![](/demo/parallel_view_people_01.png)
![](/demo/gh_demo_output/ex05b.png)
![](/demo/gh_demo_output/ex04b.png)

## Overview
Adding entourages into architectural illustrations can be time-consuming, especially for larger-scale projects. Auto Entourage for Rhino/Grasshopper aims to speed up your visualization workflow by loading entourage images (.png images with transparent background) directly into Rhino, such that entourages can be rendered alongside you 3d model.

## Plugin
The plugin consists of two components: `imgCrop` and `AutoEntourage`. The preprocess images by cropping out empty margins while the second one loads them into Rhino.

## Usage
- Download plugin into Grasshopper's components folder. Restart Rhino/Grasshopper and launch the components using shortcuts `crop` and `ae`. Alternatively, locate the components in "display" -> "preview" in the grasshopper menu. 

- Use `imgCrop` to batch preprocess images by specifying a `path` to the image folder, and `out` as a destinate to save the processed images. 

- Use `AutoEntourage` to load processed entourages into Rhino by specifying a `path` to the image folder, a set of anchor `point` to locate the entourages, as well as the `imgheight` for scaling their heights.

## Notes
- Run `imgCrop` once to preprocess images and reuse them for all future projects.
- `AutoEntourage` will take items, lists or trees as input. (With the exception of `layerName` input). You can expect the component to behave similarly to other default Grasshopper components.
- When using `AutoEngourage`, as long as the inputs are unchange,  you can `load` entourages once, and use `orient` to align entourages to different views.

## Disclaimer
The plugin had been tested for both Rhino/Grasshopper 6 and 7 on Windows 10.

## Known Issues
- `orient` in `raytrace` mode occasionally behaves incorrectly. For now, reload entourages as a workaround or simply reorient in less computationally intensive display modes.
- `orient` may cause Rhino viewports to freeze in Rhino 6.23 and 7.3

## TODO
- Add supprot for vector entourages
- Add a new component to enable users greater control in how entourages are loaded.
