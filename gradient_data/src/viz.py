def plot_surf_stat_map(coords, faces, stat_map=None,
        elev=0, azim=0,
        cmap='jet',
        threshold=None, bg_map=None,
        mask=None,
        bg_on_stat=False,
        alpha='auto',
        vmax=None, symmetric_cbar="auto", returnAx=False,
        figsize=(14,11), label=None, lenient=None,
        **kwargs):

    ''' Visualize results on cortical surface using matplotlib'''
    #sns.set_style("white", {'axes.grid' : False})
    #sns.set_context("notebook", font_scale=1.5)    
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.tri as tri
    from mpl_toolkits.mplot3d import Axes3D

    # load mesh and derive axes limits
    faces = np.array(faces, dtype=int)
    limits = [coords.min(), coords.max()]

    # set alpha if in auto mode
    if alpha == 'auto':
        if bg_map is None:
            alpha = .5
        else:
            alpha = 1

    # if cmap is given as string, translate to matplotlib cmap
    if type(cmap) == str:
        cmap = plt.cm.get_cmap(cmap)

    # initiate figure and 3d axes
    if figsize is not None:
        fig = plt.figure(figsize=figsize)
    else:
        fig = plt.figure()

    fig.patch.set_facecolor('white')
    ax1 = fig.add_subplot(111, projection='3d', xlim=limits, ylim=limits)
    ax1.view_init(elev=elev, azim=azim)
    #ax1.set_axis_off()
    ax1.grid(False)
    #ax1.set_frame_on(False)
    #ax1.axes.get_yaxis().set_visible(False)
    #ax1.axes.get_xaxis().set_visible(False)
    #plt.axis('off')
    #ax = plt.gca(projection='3d') 
    #ax1._axis3don = False
    
    # plot mesh without data
    p3dcollec = ax1.plot_trisurf(coords[:, 0], coords[:, 1], coords[:, 2],
                                triangles=faces, linewidth=0.,
                                antialiased=False,
                                color='white')

    
    if mask is not None:
        cmask = np.zeros(len(coords))
        cmask[mask] = 1
        cutoff = 2
        if lenient:
            cutoff = 0
        fmask = np.where(cmask[faces].sum(axis=1) > cutoff)[0]
        
    # If depth_map and/or stat_map are provided, map these onto the surface
    # set_facecolors function of Poly3DCollection is used as passing the
    # facecolors argument to plot_trisurf does not seem to work
    if bg_map is not None or stat_map is not None:

        face_colors = np.ones((faces.shape[0], 4))
        face_colors[:, :3] = .5*face_colors[:, :3]

        if bg_map is not None:
            bg_data = bg_map
            if bg_data.shape[0] != coords.shape[0]:
                raise ValueError('The bg_map does not have the same number '
                                 'of vertices as the mesh.')
            bg_faces = np.mean(bg_data[faces], axis=1)
            bg_faces = bg_faces - bg_faces.min()
            bg_faces = bg_faces / bg_faces.max()
            face_colors = plt.cm.gray_r(bg_faces)

        # modify alpha values of background
        face_colors[:, 3] = alpha*face_colors[:, 3]

        if stat_map is not None:
            stat_map_data = stat_map
            stat_map_faces = np.mean(stat_map_data[faces], axis=1)
            if label:
                stat_map_faces = np.median(stat_map_data[faces], axis=1)

            # Call _get_plot_stat_map_params to derive symmetric vmin and vmax
            # And colorbar limits depending on symmetric_cbar settings
            cbar_vmin, cbar_vmax, vmin, vmax = \
                _get_plot_stat_map_params(stat_map_faces, vmax,
                                          symmetric_cbar, kwargs)

            if threshold is not None:
                kept_indices = np.where(abs(stat_map_faces) >= threshold)[0]
                stat_map_faces = stat_map_faces - vmin
                stat_map_faces = stat_map_faces / (vmax-vmin)
                if bg_on_stat:
                    face_colors[kept_indices] = cmap(stat_map_faces[kept_indices]) * face_colors[kept_indices]
                else:
                    face_colors[kept_indices] = cmap(stat_map_faces[kept_indices])
            else:
                stat_map_faces = stat_map_faces - vmin
                stat_map_faces = stat_map_faces / (vmax-vmin)
                if bg_on_stat:
                    if mask is not None:
                        face_colors[fmask,:] = cmap(stat_map_faces)[fmask,:] * face_colors[fmask,:]
                    else:
                        face_colors = cmap(stat_map_faces) * face_colors
                else:
                    face_colors = cmap(stat_map_faces)

        p3dcollec.set_facecolors(face_colors)

    ax1.set_axis_off()
    
    if returnAx == True:
        return fig, ax
    else:
        return fig

def _get_plot_stat_map_params(stat_map_data, vmax, symmetric_cbar, kwargs,
    force_min_stat_map_value=None):
    
    import numpy as np

    '''
    Helper function copied from nilearn to force symmetric colormaps
    https://github.com/nilearn/nilearn/blob/master/nilearn/plotting/img_plotting.py#L52
    '''
    # make sure that the color range is symmetrical
    if vmax is None or symmetric_cbar in ['auto', False]:
        # Avoid dealing with masked_array:
        if hasattr(stat_map_data, '_mask'):
            stat_map_data = np.asarray(
                    stat_map_data[np.logical_not(stat_map_data._mask)])
        stat_map_max = np.nanmax(stat_map_data)
        if force_min_stat_map_value == None:
            stat_map_min = np.nanmin(stat_map_data)
        else:
            stat_map_min = force_min_stat_map_value
    if symmetric_cbar == 'auto':
        symmetric_cbar = stat_map_min < 0 and stat_map_max > 0
    if vmax is None:
        vmax = max(-stat_map_min, stat_map_max)
    if 'vmin' in kwargs:
        raise ValueError('this function does not accept a "vmin" '
            'argument, as it uses a symmetrical range '
            'defined via the vmax argument. To threshold '
            'the map, use the "threshold" argument')
    vmin = -vmax
    if not symmetric_cbar:
        negative_range = stat_map_max <= 0
        positive_range = stat_map_min >= 0
        if positive_range:
            cbar_vmin = 0
            cbar_vmax = None
        elif negative_range:
            cbar_vmax = 0
            cbar_vmin = None
        else:
            cbar_vmin = stat_map_min
            cbar_vmax = stat_map_max
    else:
        cbar_vmin, cbar_vmax = None, None
    return cbar_vmin, cbar_vmax, vmin, vmax

def showSurf(input_data, surf, sulc, cort, showall=None, output_file=None):
    f = plot_surf_stat_map(surf[0], surf[1], bg_map=sulc, mask=cort, stat_map=input_data, bg_on_stat=True, azim=0)
    plt.show()
    if output_file:
        count = 0
        f.savefig(('fig.%s.' + output_file) % str(count))
        count += 1
    f = plot_surf_stat_map(surf[0], surf[1], bg_map=sulc, mask=cort, stat_map=input_data, bg_on_stat=True, azim=180)
    plt.show()
    if output_file:
        f.savefig(('fig.%s.' + output_file) % str(count))
        count += 1
    if showall:
        f = plot_surf_stat_map(surf[0], surf[1], bg_map=sulc, mask=cort, stat_map=input_data, bg_on_stat=True, azim=90)
        plt.show()
        if output_file:
            f.savefig(('fig.%s.' + output_file) % str(count))
            count += 1
        f = plot_surf_stat_map(surf[0], surf[1], bg_map=sulc, mask=cort, stat_map=input_data, bg_on_stat=True, azim=270)
        plt.show()
        if output_file:
            f.savefig(('fig.%s.' + output_file) % str(count))
            count += 1
        f = plot_surf_stat_map(surf[0], surf[1], bg_map=sulc, mask=cort, stat_map=input_data, bg_on_stat=True, elev=90)
        plt.show()
        if output_file:
            f.savefig(('fig.%s.' + output_file) % str(count))
            count += 1
        f = plot_surf_stat_map(surf[0], surf[1], bg_map=sulc, mask=cort, stat_map=input_data, bg_on_stat=True, elev=270)
        plt.show()
        if output_file:
            f.savefig(('fig.%s.' + output_file) % str(count))
            count += 1

