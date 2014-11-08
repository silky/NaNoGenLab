#!/usr/bin/env python

from optparse import OptionParser
import os
import random
import sys

from PIL import Image


def cutup(filename, options):
    image = Image.open(filename)
    print image
    dirname = os.path.basename(filename) + '.dir'

    os.mkdir(dirname)

    (width, height) = image.size

    # FIXME: iteratively look for too-dark rectangles around the edge of
    # the image and remove them one by one instead.  but this is OK for now

    margin_left = int(width * 0.05)
    margin_right = int(width * 0.95)
    margin_top = int(height * 0.05)
    margin_bottom = int(height * 0.95)
 
    region = image.crop((margin_left, margin_top, margin_right, margin_bottom))
    image = region.copy()
    contrast = image.copy()

    (width, height) = image.size

    light_rows = []

    # FIXME: throw the image through an (almost-)max-contrast filter first;
    # that should make it easier to work on a wide range of images of varying
    # contrast levels

    for y in xrange(0, height):
        if y % 100 == 0:
            print "row %s/%s" % (y, height)
        light_pixels = 0
        for x in xrange(0, width):
            pixel = image.getpixel((x, y))
            light = False
            if pixel > 175:  # 150 ?
                light = True
            if light:
                if options.debug:
                    contrast.putpixel((x, y), 255)
                light_pixels += 1
            else:
                if options.debug:
                    contrast.putpixel((x, y), 0)
                pass
        if (light_pixels / (width * 1.0)) > 0.96:
            light_rows.append(y)
            #for x in xrange(0, width):
            #    image.putpixel((x, y), 128)

    if options.debug:
        contrast.save(os.path.join(dirname, "contrast.png"))

    cuttable_ribbons = []  # list of (y, thickness) tuples
    thickness = None
    start_y = None
    previous_light_y = None
    for light_y in light_rows:
        if previous_light_y is None:
            thickness = 1
            start_y = light_y
            previous_light_y = light_y
        elif previous_light_y == light_y - 1:
            thickness += 1
            previous_light_y = light_y
        else:
            previous_light_y = None
            cuttable_ribbons.append((start_y, thickness))

    # reduce ribbon thicknesses
    margin = 4  # how much whitespace you want around darkpixelness?
    cuttable_ribbons = [
        (start_y + margin, thickness - margin * 2)
        for (start_y, thickness) in cuttable_ribbons
        if thickness > margin * 2
    ]
    # FIXME: we could / should retain the insufficiently-thick ones?

    if options.debug:
        print cuttable_ribbons
        for ribbon in cuttable_ribbons:
            for y in xrange(ribbon[0], ribbon[0] + ribbon[1]):
                for x in xrange(0, width):
                    image.putpixel((x, y), 0)

    # compute the crop-areas BETWEEN the cuttable ribbons
    crop_y = 0
    crop_areas = []

    for (start_y, thickness) in cuttable_ribbons:
        crop_areas.append(
            (0, crop_y, width, start_y)
        )
        crop_y = start_y + thickness

    crop_areas.append(
        (0, crop_y, width, height)
    )

    for (crop_num, crop_area) in enumerate(crop_areas):
        region = image.crop(crop_area)
        print "writing %s to crop%s.png" % (crop_area, crop_num)
        region.save(os.path.join(dirname, "crop%s.png" % crop_num))

    if options.debug:
        image.save(os.path.join(dirname, "cutlines.png"))


def main(argv):
    optparser = OptionParser(__doc__)
    optparser.add_option("--debug", action='store_true', default='False',
                         help="output debuging info")
    (options, args) = optparser.parse_args(argv[1:])

    for filename in args:
        cutup(filename, options)


if __name__ == '__main__':
    import sys
    main(sys.argv)