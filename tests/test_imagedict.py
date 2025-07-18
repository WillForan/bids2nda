import json
import os
import shutil

import bids2nda


def test_potential_json_noses():
    """where bids metadata could be for a specific sequence without a session label"""
    noses = bids2nda.get_potential_jsons(
        "bids", "bids/sub-1/func/sub-1_task-rest_acq-fast_bold.json"
    )
    assert noses == [
        "bids/task-rest_acq-fast_bold.json",
        "bids/sub-1/sub-1_task-rest_acq-fast_bold.json",
        "bids/sub-1/func/sub-1_task-rest_acq-fast_bold.json",
    ]


def test_potential_json_ses():
    """where bids metadata could be for a specific sequence with a session label"""
    ses = bids2nda.get_potential_jsons(
        "bids", "bids/sub-a/ses-1/func/sub-a_ses-1_task-rest_acq-fast_bold.json"
    )
    assert ses == [
        "bids/task-rest_acq-fast_bold.json",
        "bids/sub-a/sub-a_task-rest_acq-fast_bold.json",
        "bids/sub-a/ses-1/sub-a_ses-1_task-rest_acq-fast_bold.json",
        "bids/sub-a/ses-1/func/sub-a_ses-1_task-rest_acq-fast_bold.json",
    ]


def test_metadata(tmpdir):
    funcdir = tmpdir.join("in/sub-a/func")
    os.makedirs(funcdir)
    ex_json = os.path.join(
        os.getcwd(), "examples/bids-noses/sub-a/func/sub-a_task-rest_bold.json"
    )

    new_json = funcdir.join("sub-a_task-rest_acq-xyz_bold.json")
    shutil.copyfile(ex_json, new_json)

    metadata = bids2nda.get_metadata_for_nifti(str(tmpdir / "in"), str(new_json))
    assert metadata.get("TaskName", "rest")  # read from json
    assert metadata.get("acq", "xyz")  # read from filename
    assert metadata.get("task", "rest")  # read from filename


def test_taskname(tmpdir):
    """
    Task name can be from bids sidecar .json
    if that doesn't exist, pull from filename
    """
    # setup new dedicated bids input dir
    funcdir = tmpdir.join("in/sub-a/func")
    os.makedirs(funcdir)
    for ext in [".json", ".nii.gz"]:
        shutil.copyfile(
            os.path.join(
                os.getcwd(), "examples/bids-noses/sub-a/func/sub-a_task-rest_bold" + ext
            ),
            funcdir.join("sub-a_task-rest_bold" + ext),
        )
    shutil.copyfile(
        os.path.join(os.getcwd(), "examples/bids-noses/participants.tsv"),
        tmpdir / "in/participants.tsv",
    )
    shutil.copyfile(
        os.path.join(os.getcwd(), "examples/bids-noses/sub-a/sub-a_scans.tsv"),
        funcdir / "../sub-a_scans.tsv",
    )

    # run
    args = bids2nda.parse_args(
        [str(tmpdir / "in/"), "examples/guid_map.txt", str(tmpdir / "out")]
    )
    imgdf = bids2nda.run(args)
    assert imgdf.shape[0] == 1
    assert imgdf.image_description[0] == "bold rest"

    #  run again with TaskName in json
    sidecar_fname = funcdir.join("sub-a_task-rest_bold.json")
    with open(sidecar_fname, "r") as f:
        sidecar = json.load(f)
    sidecar["TaskName"] = "NOTREST"
    with open(sidecar_fname, "w") as f:
        f.write(json.dumps(sidecar))
    imgdf = bids2nda.run(args)
    assert imgdf.shape[0] == 1
    assert imgdf.image_description[0] == "bold NOTREST"
