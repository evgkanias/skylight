import numpy as np
import numpy.linalg as la
from utils import pix2sph, Width as W, Height as H


def vec2sph(vec):
    """
    Transforms a cartessian vector to spherical coordinates.
    :param vec:     the cartessian vector
    :return theta:  elevation
    :return phi:    azimuth
    :return rho:    radius
    """
    rho = la.norm(vec, axis=-1)  # length of the radius

    if vec.ndim == 1:
        vec = vec[np.newaxis, ...]
        if rho == 0:
            rho = 1.
    else:
        rho = np.concatenate([rho[..., np.newaxis]] * vec.shape[1], axis=-1)
        rho[rho == 0] = 1.
    v = vec / rho  # normalised vector

    phi = np.arctan2(v[:, 0], v[:, 1])  # azimuth
    theta = np.arccos(v[:, 2])  # elevation

    # theta, phi = sphadj(theta, phi)  # bound the spherical coordinates
    return np.asarray([theta, phi, rho[:, -1]])


def cubebox_angles(side):
    if side == "left":
        y = np.linspace(1, -1, W, endpoint=False)
        z = np.linspace(1, -1, H, endpoint=False)
        y, z = np.meshgrid(y, z)
        x = -np.ones(W * H)
    elif side == "front":
        x = np.linspace(-1, 1, W, endpoint=False)
        z = np.linspace(1, -1, H, endpoint=False)
        x, z = np.meshgrid(x, z)
        y = -np.ones(W * H)
    elif side == "right":
        y = np.linspace(-1, 1, W, endpoint=False)
        z = np.linspace(1, -1, H, endpoint=False)
        y, z = np.meshgrid(y, z)
        x = np.ones(W * H)
    elif side == "back":
        x = np.linspace(1, -1, W, endpoint=False)
        z = np.linspace(1, -1, H, endpoint=False)
        x, z = np.meshgrid(x, z)
        y = np.ones(W * H)
    elif side == "top":
        x = np.linspace(-1, 1, W, endpoint=False)
        y = np.linspace(1, -1, W, endpoint=False)
        x, y = np.meshgrid(x, y)
        z = np.ones(W * W)
    elif side == "bottom":
        x = np.linspace(-1, 1, W, endpoint=False)
        y = np.linspace(-1, 1, W, endpoint=False)
        x, y = np.meshgrid(x, y)
        z = -np.ones(W * W)
    else:
        x, y, z = np.zeros((3, H * W))
    vec = np.stack([x.reshape(H * W), y.reshape(H * W), z.reshape(H * W)]).T
    theta, phi, _ = vec2sph(vec)
    return theta, phi


def cubebox(sky, side):
    theta, phi = cubebox_angles(side)
    L, DOP, AOP = sky.get_features(theta, phi)
    L = L.reshape((W, H))
    DOP[np.isnan(DOP)] = -1
    DOP = DOP.reshape((W, H))
    AOP = AOP.reshape((W, H))

    L_cube = np.zeros((W, H, 3))
    L_cube[..., 0] = L + (1. - L) * .05  # deep sky blue * .53
    L_cube[..., 1] = L + (1. - L) * .53  # deep sky blue * .81
    L_cube[..., 2] = L + (1. - L) * .79  # deep sky blue * .92
    L_cube = np.clip(L_cube, 0, 1)

    DOP_cube = np.zeros((W, H, 3))
    DOP_cube[..., 0] = DOP * .53 + (1. - DOP)
    DOP_cube[..., 1] = DOP * .81 + (1. - DOP)
    DOP_cube[..., 2] = DOP * 1.0 + (1. - DOP)
    DOP_cube = np.clip(DOP_cube, 0, 1)

    AOP_cube = AOP % np.pi
    AOP_cube = np.clip(AOP_cube, 0, np.pi)

    return L_cube, DOP_cube, AOP_cube


def skydome(sky):
    x, y = np.arange(W), np.arange(H)
    x, y = np.meshgrid(x, y)
    x, y = x.flatten(), y.flatten()
    theta, phi = pix2sph(np.array([x, y]), H, W)
    sky_L, sky_DOP, sky_AOP = sky.get_features(theta, phi)
    sky_L = np.clip(sky_L, 0, 1)
    sky_DOP = np.clip(sky_DOP, 0, 1)

    L = np.zeros((W, H, 3))
    L[x, y, 0] = sky_L + (1. - sky_L) * .05
    L[x, y, 1] = sky_L + (1. - sky_L) * .53
    L[x, y, 2] = sky_L + (1. - sky_L) * .79

    DOP = np.zeros((W, H, 3))
    DOP[x, y, 0] = sky_DOP * .53 + (1. - sky_DOP)
    DOP[x, y, 1] = sky_DOP * .81 + (1. - sky_DOP)
    DOP[x, y, 2] = sky_DOP * 1.0 + (1. - sky_DOP)

    AOP = sky_AOP % np.pi
    AOP = np.clip(AOP, 0, np.pi).reshape((W, H))

    return L, DOP, AOP
