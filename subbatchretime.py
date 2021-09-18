import argparse
import os
import datetime
        

class SubBatchRetime():
    VALID_EXTENSIONS = ['.srt'] 
    
    def __init__(self, seconds_offset, sub_dir='Subtitles'):
        """
        Parameters
        ----------
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
        line_list = self.__chunk_sub_idx_to_list(self._file_to_line_list(file)) 
        assert delimiter in line_list[0][1], 'Column index 1 does not match time str format expected.'
        
        for i, row in enumerate(line_list):
            time_str = row[time_col_idx]
            start, stop = self._srt_time_to_seconds(time_str)
            start += self.offset
            stop += self.offset
            
            start_str = self._seconds_to_timestr(start)
            stop_str = self._seconds_to_timestr(stop)
            line_list[i][time_col_idx] = start_str+delimiter+stop_str
            
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
 
        save_path = os.path.join(save_dir, os.path.basename(file))
        self._export_line_list(save_path, line_list)
        
    def _export_line_list(self, filename, line_list):
        
        export = []    
        for line in line_list:
            for part in line:
                export += [part + '\n']  
            export += ['\n']
        
        with open(filename, 'w', encoding="utf-8-sig") as file:           
            file.writelines(export)
            
    def _seconds_to_timestr(self, s):
        return str(datetime.timedelta(seconds=s))[:-3].replace('.', ',')
    
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
    
    def __chunk_sub_idx_to_list(self, sub_line_list):
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



 
