import argparse
import os
import numpy as np
        

class SubBatchRetime():
    VALID_EXTENSIONS = ['.srt'] 
    
    def __init__(self, seconds_offset, sub_dir='Subtitles'):
        """
        Parameters
        ----------
        seconds_offset : float or list
            if float: seconds to offset, use negative values to shift closer to the beginning
            if list: list should be a list of tuples
                (start_time, delta)
                start_time=at what time in seconds to start shifting by delta
                delta= amount of time to shift by in seconds
        sub_dir : str
            path of directory containing one or multiple subtitle files
        """
        for path in [sub_dir]:
            assert os.path.exists(path), f'Path provided does not exist. {path}. Either create {path} director and add subtitles to it or pass in a different valid path.'
            
        self.sub_dir = sub_dir
        self.sub_files = sorted([os.path.join(sub_dir, f) for f in os.listdir(sub_dir) if f.endswith('|'.join(self.VALID_EXTENSIONS))])
        self.offset = seconds_offset
        
        # Retime all files & place in Retimed directory
        for file in self.sub_files:
            self._fix_single_file(file)
        
    def _fix_single_file(self, file, time_col_idx=1, delimiter=' --> ', save_dir='Retimed'):
        line_list = self._chunk_sub_idx_to_list(self._file_to_line_list(file)) 
        assert delimiter in line_list[0][1], 'Column index 1 does not match time str format expected.'
        
        multi_time = type(self.offset) == list
        multi_idx = 0
        
        if multi_time:
            self.offset = self._optimize_retiming(line_list)
        
        offset = 0 if multi_time else self.offset
        
        for i, row in enumerate(line_list):
            time_str = row[time_col_idx]
            start, stop = self._srt_time_to_seconds(time_str)
            
            if multi_time and multi_idx < len(self.offset):
                delta_start, delta = self.offset[multi_idx]
                if start >= delta_start:
                    offset = delta
                    multi_idx += 1
            
            start += offset
            stop += offset
            
            assert start > 0, 'Delta time too large, negative start time created.'
            
            start_str = self._seconds_to_timestr(start)
            stop_str = self._seconds_to_timestr(stop)
            line_list[i][time_col_idx] = start_str+delimiter+stop_str
            
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
 
        save_path = os.path.join(save_dir, os.path.basename(file))
        self._export_line_list(save_path, line_list)
        
    def _optimize_retiming(self, line_list):
        gaps = self._get_delta_times(line_list)

        best_retime = []
        for cnt, (t, total_delta) in enumerate(self.offset):
            delta = total_delta - sum([d for _, d in self.offset[:cnt]])

            gap_times, gap_deltas = zip(*[(ti, d) for ti, d in gaps if d > abs(delta)])

            if len(gap_times) == 0:
                print(f'No time gap large enough for requested shift of {delta}. This will result in overlap of times in the subtitle file.')
                best_retime += [(gap_times[idx], gap_deltas[idx])]
            else:
                idx = np.argmin(np.array(gap_times) - abs(delta))
                best_retime += [(gap_times[idx], total_delta)]

                # Time no longer available, so remove from options
                gaps.pop(gaps.index((gap_times[idx], gap_deltas[idx])))
                
        return best_retime
        
    def _get_delta_times(self, line_list, time_col_idx=1):
        time_gaps = []

        prev_stop = 0
        for row in line_list:
            time_str = row[time_col_idx]
            start, stop = self._srt_time_to_seconds(time_str)
            
            if start - prev_stop > 0:
                delta = start - prev_stop
                time_gaps += [(start - delta, delta)]
            prev_stop = stop
        return time_gaps
        
    def _export_line_list(self, filename, line_list):
        
        export = []    
        for line in line_list:
            for part in line:
                export += [part + '\n']  
            export += ['\n']
        
        with open(filename, 'w', encoding="utf-8-sig") as file:           
            file.writelines(export)
            
    def _seconds_to_timestr(self, s):
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        millsec = int(1000*(seconds - int(seconds)))
        return '{:02}:{:02}:{:02},{:03}'.format(int(hours), int(minutes), int(seconds), millsec)
    
    def _srt_time_to_seconds(self, time_line):
        def timestr_to_sec(time_str):
            h, m, s_str = time_str.split(':')
            s, ms = s_str.split(',')
            return int(h)*60*60 + int(m)*60 + int(s) + int(ms)/1000 
        
        start_time_str, stop_time_str = time_line.split(' --> ')
        start_time = timestr_to_sec(start_time_str)
        stop_time = timestr_to_sec(stop_time_str)
        
        return start_time, stop_time
                      
    def _file_to_line_list(self, filename, encoding='utf-8-sig'):
        line_list = []
        with open(filename, 'r', encoding=encoding) as file:
            for line in file:
                line_list += [line.replace('\n', '')]
        return line_list
    
    def _chunk_sub_idx_to_list(self, sub_line_list):
        """
            Pass in a list where each line is a line in the subtitle file
            Example:
            ['1', '00:00:00,000 --> 00:00:04,430', 'おはようございます', '2', ...]

            return a list where each list item is another list where each item is specific to its index
            Example:
            [['1', '00:00:00,000 --> 00:00:04,430', 'おはようございます'], ['2', ...], ...]
        """
        lines_indexed = []
        tmp = []
        for i, line in enumerate(sub_line_list):
            if line == '':
                continue

            tmp += [line]
            if len(tmp) > 3:
                digit, timestamp = tmp[-2:]
                if digit.strip().isdigit() and '-->' in timestamp:
                    lines_indexed += [tmp[:-2]]
                    tmp = tmp[-2:]
        return lines_indexed
        
    def __len__(self):
        return len(self.sub_files)



 

