# Auto Entourage
Auto Entourage is a small Grasshopper plugin for loading entourage images(.png format) from an image folder into Rhino.

## Overview
Adding entourages into architectural illustrations can be time-consuming, especially for larger-scale projects. Auto Entourage for Rhino/Grasshopper aims to speed up your visualization workflow by loading entourage images (.png images with transparent background) directly into Rhino, such that entourages can be rendered alongside you 3d model.

## Plugin
The plugin consists of two components: `imgCrop` and `AutoEntourage`. The preprocess images by cropping out empty margins while the second loads them into Rhino.

## Usage
- Download plugin into Grasshopper's components folder. Restart Rhino/Grasshopper and launch the components using shortcuts `crop` and `ae`. Alternatively locate the components in "display" -> "preview" in the grasshopper menu. 

- Use `imgCrop` to batch preprocess images by specifying a `path` to the image folder, and `out` as a destinate to save the processed images. 

- Use `AutoEntourage` to load processed entourages into Rhino by specifying a `path` to the image folder, a set of anchor `point` to locate the entourages, as well as the `imgheight` for scaling their heights.

## Notes
- Run `imgCrop` once to preprocess images and reuse them for all future projects.
- `AutoEntourage` will take items, lists or trees as input. (With the exception of `layerName`). You can expect the component to behave similarly to other default Grasshopper components.

## Disclaimer
The plugin had only been tested for Rhino 6 on Windows 10.

## Known Issues
- `orient` in `raytrace` mode will occasionally mis-orient the entourages. For now, reload entourages as a workaround or simply reorient in less compuationally intensive display modes. 

## Next Steps
- vector entourages support
- a new components to enable users greater control in how entourages are loaded.
