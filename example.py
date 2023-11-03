import os
import matplotlib.pyplot as plt
import numpy as np
import pylops
from solartom import project_3d
from solartom.ops import TomoOp

def z_rotation_matrix_3d(angle):
    return np.array([[[np.cos(angle), np.sin(angle), 0],
                      [-np.sin(angle), np.cos(angle), 0],
                      [0, 0, 1]]])

if __name__ == "__main__":
    print("Test started")
    os.makedirs("test_output/", exist_ok=True)

    num_angles = 100
    angles = np.linspace(0, np.pi, num_angles) + np.pi/60

    radius = 300
    img_size = 100
    cube_size = 100

    # create a ground truth model of a hollow cube
    densities = np.zeros((cube_size, cube_size, cube_size), dtype=np.float32)
    densities[30:-30, 30:-30, 30:-30] = 100
    densities[40:-40, 40:-40, 40:-40] = 0
    mask = np.ones((cube_size, cube_size, cube_size), dtype=bool)
    # mask[43:-43, 43:-43, 43:-43] = False


    # set up coordinate system
    b = (-cube_size / 2, -cube_size / 2, -cube_size / 2)
    delta = (1.0, 1.0, 1.0)
    path_distance = 500.0

    # do all the forward projections to make test data
    norms, xs, ys, zs, ds, imgs = [], [], [], [], [], []
    for angle in angles:
        t_angle = -angle + np.pi/2 

        img_x = np.arange(img_size) - img_size / 2
        img_y = np.zeros((img_size, img_size))
        img_z = np.arange(img_size) - img_size / 2
        img_x, img_z = np.meshgrid(img_x, img_z)

        img_x, img_y, img_z = img_x.flatten(), img_y.flatten(), img_z.flatten()

        R = z_rotation_matrix_3d(t_angle)
        coords = (R @ np.stack([img_x, img_y, img_z]))[0]
        img_x, img_y, img_z = coords[0], coords[1], coords[2]
        img_x = radius * np.cos(angle) + img_x  
        img_y = radius * np.sin(angle) + img_y  

        xx = img_x.reshape((img_size, img_size)).astype(np.float32)
        yy = -img_y.reshape((img_size, img_size)).astype(np.float32)
        zz = img_z.reshape((img_size, img_size)).astype(np.float32)

        v1 = np.array([xx[0, 1] - xx[0, 0], yy[0, 1] - yy[0, 0], zz[0, 1] - zz[0, 0]])
        v2 = np.array([xx[1, 0] - xx[0, 0], yy[1, 0] - yy[0, 0], zz[1, 0] - zz[0, 0]])
        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        norm = normal  
        norm[norm == 0] = 1E-6
        norms.append(norm)

        d = 500
        img = project_3d(xx, yy, zz, densities, mask, b, delta, norm, d)
        xs.append(xx)
        ys.append(yy)
        zs.append(zz)
        ds.append(d)
        imgs.append(img.astype(np.float32))
    imgs = np.array(imgs)

    # show forward projections
    for angle, img in zip(angles, imgs):
        fig, ax = plt.subplots()
        im = ax.imshow(img)
        fig.colorbar(im)
        fig.savefig(f"test_output/{int(np.rad2deg(angle)):03d}.png")
        plt.close()

    # set up linear operator
    op = TomoOp(xs, ys, zs, norms, ds, b, delta, densities.shape, mask, dtype=np.float32)

    # do optimization
    Dop = [
        pylops.FirstDerivative(
            (cube_size, cube_size, cube_size),
            axis=0, edge=False, kind="backward", dtype=np.float32
        ),
        pylops.FirstDerivative(
            (cube_size, cube_size, cube_size),
            axis=1, edge=False, kind="backward", dtype=np.float32
        ),
        pylops.FirstDerivative(
            (cube_size, cube_size, cube_size), 
            axis=2, edge=False, kind="backward", dtype=np.float32
        )
    ]
   
    # model = pylops.optimization.basic.lsqr(op, imgs.flatten(), niter=10, show=True)[0]
    model = pylops.optimization.leastsquares.regularized_inversion(op, 
                                                                   imgs.flatten(), 
                                                                   Dop, 
                                                                   iter_lim=10, 
                                                                   show=True)[0]
    model = model.reshape(densities.shape)


    # visualize a comparison of the ground truth and learned model cubes
    limit = 150
    
    for i in range(cube_size):
        fig, axs = plt.subplots(ncols=2)
        im = axs[0].imshow(densities[i, :, :], vmin=0, vmax=limit)
        fig.colorbar(im)
        im = axs[1].imshow(model[i, :, :], vmin=0, vmax=limit)
        fig.colorbar(im)
        fig.show()
        fig.savefig(f"test_output/comparison_0_{i:03d}.png")
        plt.close()
        
    for i in range(cube_size):
        fig, axs = plt.subplots(ncols=2)
        im = axs[0].imshow(densities[:, i, :], vmin=0, vmax=limit)
        fig.colorbar(im)
        im = axs[1].imshow(model[:, i, :], vmin=0, vmax=limit)
        fig.colorbar(im)
        fig.show()
        fig.savefig(f"test_output/comparison_1_{i:03d}.png")
        plt.close()
        
        
    for i in range(cube_size):
        fig, axs = plt.subplots(ncols=2)
        im = axs[0].imshow(densities[:, :, i], vmin=0, vmax=limit)
        fig.colorbar(im)
        im = axs[1].imshow(model[:, :, i], vmin=0, vmax=limit)
        fig.colorbar(im)
        fig.show()
        fig.savefig(f"test_output/comparison_2_{i:03d}.png")
        plt.close()

    print("Test finished")