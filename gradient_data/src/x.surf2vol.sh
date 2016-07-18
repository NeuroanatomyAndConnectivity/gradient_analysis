#!/bin/bash

caret_command -file-convert -sc -is GS gradient_data/templates/Q1-Q6_R440.L.midthickness.32k_fs_LR.surf.gii \
  -os CARET gradient_data/templates/fiducialL.coord gradient_data/templates/closedL.topo FIDUCIAL CLOSED \
  -spec gradient_data/templates/fileL.spec -struct LEFT

caret_command -file-convert -sc -is GS gradient_data/templates/Q1-Q6_R440.R.midthickness.32k_fs_LR.surf.gii \
  -os CARET gradient_data/templates/fiducialR.coord gradient_data/templates/closedR.topo FIDUCIAL CLOSED \
  -spec gradient_data/templates/fileR.spec -struct RIGHT


for i in 0 1 2 3 4 5 6 7 8 9; do

  let ind="${i} + 1" 

  # wb_command -cifti-merge gradient_data/embedded/ciftis/hcp.embed.${i}.dscalar.nii -cifti gradient_data/embedded/ciftis/hcp.embed.dscalar.nii -column ${ind}

  #wb_command -cifti-separate gradient_data/embedded/ciftis/hcp.embed.${i}.dscalar.nii COLUMN -metric CORTEX_LEFT gradient_data/embedded/ciftis/hcp.embed.${i}.L.metric
  #wb_command -cifti-separate gradient_data/embedded/ciftis/hcp.embed.${i}.dscalar.nii COLUMN -metric CORTEX_RIGHT gradient_data/embedded/ciftis/hcp.embed.${i}.R.metric

  #caret_command -volume-create-in-stereotaxic-space FNIRT-222 gradient_data/embedded/volumes/volume.${i}.L.nii
  #caret_command -surface-to-volume gradient_data/templates/fiducialL.coord gradient_data/templates/closedL.topo \
  #  gradient_data/embedded/ciftis/hcp.embed.${i}.L.metric 1 gradient_data/embedded/volumes/volume.${i}.L.nii \
  #  -inner -1.5 -outer 1.5 -step 0.3

  #caret_command -volume-create-in-stereotaxic-space FNIRT-222 gradient_data/embedded/volumes/volume.${i}.R.nii
  #caret_command -surface-to-volume gradient_data/templates/fiducialR.coord gradient_data/templates/closedR.topo \
  #  gradient_data/embedded/ciftis/hcp.embed.${i}.R.metric 1 gradient_data/embedded/volumes/volume.${i}.R.nii \
  #  -inner -1.5 -outer 1.5 -step 0.3

  # combine:
  fslmaths gradient_data/embedded/volumes/volume.${i}.L.nii \
    -add gradient_data/embedded/volumes/volume.${i}.R.nii gradient_data/embedded/volumes/volume.${i}.nii
  fslmaths gradient_data/embedded/volumes/volume.${i}.L.nii \
    -add gradient_data/embedded/volumes/volume.${i}.R.nii -abs -bin gradient_data/embedded/volumes/mask.${i}.nii
  p=`fslstats gradient_data/embedded/volumes/volume.${i}.nii -R | awk '{print $1;}'`  
  fslmaths gradient_data/embedded/volumes/mask.${i}.nii -mul ${p#-} gradient_data/embedded/volumes/mask.${i}.nii
  fslmaths gradient_data/embedded/volumes/volume.${i}.nii.gz \
    -add gradient_data/embedded/volumes/mask.${i}.nii gradient_data/embedded/volumes/volume.${i}.nii.gz

  # extract masks:
  mkdir gradient_data/embedded/volumes/emb_masks_${i}
  for j in `seq 0 5 95`; do
    let k="${j} + 5"
    fslmaths gradient_data/embedded/volumes/volume.${i}.nii \
      -thr `fslstats gradient_data/embedded/volumes/volume.${i}.nii -P ${j}` \
      -uthr `fslstats gradient_data/embedded/volumes/volume.${i}.nii -P ${k}` \
      -bin gradient_data/embedded/volumes/emb_masks_${i}/volume_$(printf %02d $j)_$(printf %02d $k).nii
  done
done
