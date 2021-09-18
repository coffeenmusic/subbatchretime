# Batch Retime Subtitles Files
Note: Only works with *.srt files

    from subbatchretime import SubBatchRetime
    sub_dir = 'Subtitles'
    sub = SubBatchRetime(sub_dir, -31.5)
    
This will export to a 'Retimed/' subdir

### Or, w/ Multiple Time Offsets
For example, if a sub needs to be offset differently after the intro.
Pass in a list of tuples [(start time of delta, delta amount)]

    retime_list = [(0, -31), (131, -89)]
    sub = SubBatchRetime(retime_list)

Note: times are not compounded, so the first offset won't be added to the second offset