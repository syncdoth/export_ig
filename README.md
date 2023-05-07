# Export Images for IG

Add padding around image, drop shadows.

# How to Use

Install packages.

```bash
pip install -r requirements.txt
```

```bash
python export_ig.py --input_path "*.jpg" --output_folder padded/ \
    --aspect_ratio 4x5 --shadow_offset 32 --radius 12 --shadow_color gray \
    --pad 100 --bg_color white \
    --n_jobs 10
```

* `input_path`: glob string for input files. When using wildcard (*), make sure to
                wrap it in quotes so that it does not get expanded by bash.
* `output_folder`: folder to contain processed images.
* `aspect_ratio`: aspect ratio of output image. Auto adjusted for portrait and landscape. Should be separated by "x".
* `shadow_offset`: offset for shadow (in pixels). negative number leads to shadow on top-left diagonal of the image.
* `radius`: blur radius for the shadow.
* `shadow_color`: can be either hex string value (with or without #) or color names in {white, black, gray}
* `bg_color`: color for the padded background.
* `pad`: amount (in pixels) to pad.
* `n_jobs`: how many threads to use.

# Examples

Before                       |  After
:---------------------------:|:-------------------------------:
![taxi](imgs/taxi.jpg)       | ![padded](imgs/taxi-padded.jpg)
