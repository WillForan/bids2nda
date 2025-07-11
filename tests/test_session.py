import bids2nda


def test_sub_extract():
    sub = bids2nda.sub_from_file('path/sub-a/ses-b/sub-a_ses-b_thing.blah')
    assert sub == 'sub-a'


def test_read_noses():
    df = bids2nda.read_participant_info('examples/bids-noses/')
    assert df.shape[0] == 2
    assert 'sex' in df.columns


def test_read_ses():
    df = bids2nda.read_participant_info('examples/bids-ses/')
    assert df.shape[0] == 4
    assert 'sex' in df.columns
    assert 'acq_time' in df.columns


def test_read_scan_date():
    date = bids2nda.read_scan_date('examples/bids-noses/sub-a/sub-a_scans.tsv', 'blah/blah/func/sub-a_task-rest_bold.nii.gz')
    assert date == '2020-12-01'
