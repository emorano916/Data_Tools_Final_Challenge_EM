import matplotlib.pyplot as plt
import numpy as np
import rasterio as rs
from rasterio.mask import mask
from shapely.geometry import Polygon
import pyproj
import re



def main():
    # bruges
    # DMS (LAT , LON) 51° 12' 33.653" N, 3° 13' 28.918" E
    # DD 51.209348, 3.2246995


    def dms2dd():
        # example: s = """0°51'56.29"S"""

        LAT, LON = map(str, input('Enter your x, y coordinates: ').split(','))
        degreesLAT, minutesLAT, secondsLAT, directionLAT = re.split('[°\'"]+', LAT)
        ddLAT = float(degreesLAT) + float(minutesLAT) / 60 + float(secondsLAT) / (60 * 60);
        if directionLAT in ('S'):
            ddLAT *= -1

        degreesLON, minutesLON, secondsLON, directionLON = re.split('[°\'"]+', LON)
        ddLON = float(degreesLON) + float(minutesLON) / 60 + float(secondsLON) / (60 * 60);
        if directionLON in ('S', 'W'):
            ddLON *= -1
        return (ddLAT, ddLON)

    x1, y1 =dms2dd()

    proj = pyproj.Transformer.from_crs(4326, 31370)

    x2, y2 = proj.transform(x1, y1)

    edgelen = 80

    #creation of the region of interest (roi), a square
    roi = Polygon([(x2 - int(edgelen / 2), y2 + int(edgelen / 2)),
                   (x2 + int(edgelen / 2), y2 + int(edgelen / 2)),
                   (x2 + int(edgelen / 2), y2 - int(edgelen / 2)),
                   (x2 - int(edgelen / 2), y2 - int(edgelen / 2))])


    with rs.open('DHMVIIDSMRAS1m_k13\GeoTIFF\DHMVIIDSMRAS1m_k13.tif') as src:
        out_image, out_transform = rs.mask.mask(src, shapes=[roi],crop=True, filled = False)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})

    with rs.open("RGB_masked.tif", "w", **out_meta) as dest:
        dest.write(out_image)


        # creation of an array

        myarray2 = np.array(out_image)

        # getting rid of the NAN value and change to numerical value
        diff_surf = np.nan_to_num(myarray2)

        # Defining of x and y
        temp_x = np.arange(diff_surf.shape[2])
        temp_y = np.arange(diff_surf.shape[1])

        # Fliping of y value
        temp_y = np.flip(temp_y, 0)

        # Creation of the meshgrid
        X_diff, Y_diff = np.meshgrid(temp_x, temp_y)

        # Definition of Z layer
        Z_diff = diff_surf[0]

        # Plot DSM in Python
        fig_dsm = plt.figure(figsize=(10, 10))

        ax = fig_dsm.add_subplot(111, projection='3d')
        ax.axis('off')

        ax.plot_surface(X_diff, Y_diff, Z_diff, rstride=1, cstride=1, linewidth=5)

        # limit of the Z height and plot of title
        ax.set_zlim3d(0, 30)
        plt.title("Digital Surface Model")

        plt.show()

if __name__ == "__main__":
    main()



